"""
نقطه ورود اصلی پروژه.
این فایل توسط GitHub Actions به صورت زمان‌بندی‌شده اجرا می‌شه.

مراحل:
1. جمع‌آوری داده از Binance برای همه کوین‌های لیست
2. محاسبه اندیکاتورهای تکنیکال (قطعی، بدون AI)
3. امتیازدهی و فیلتر بهترین سیگنال‌ها
4. تولید توضیح نهایی با LLM رایگان (فقط برای سیگنال‌های برتر)
5. ارسال به تلگرام + ذخیره در تاریخچه
"""

from config.settings import COIN_LIST, MAX_DAILY_SIGNALS, MIN_SCORE_TO_SIGNAL
from src.data_collector import get_exchange, collect_symbol_data
from src.indicators import compute_indicators, summarize_latest, get_trend_direction
from src.scoring_engine import score_symbol, calculate_risk_levels, rank_and_filter_signals
from src.crew_agents import generate_explanation_safe
from src.telegram_sender import send_telegram_message
from src.storage import save_signal_record, count_signals_today


def analyze_symbol(exchange, symbol: str) -> dict | None:
    """تحلیل کامل یک نماد و برگردوندن نتیجه امتیازدهی"""
    data = collect_symbol_data(exchange, symbol)
    if data is None:
        return None

    df_with_indicators = compute_indicators(data["df_main"])
    if len(df_with_indicators) < 30:
        return None

    latest = summarize_latest(df_with_indicators)
    trend = get_trend_direction(data["df_higher"])

    result = score_symbol(symbol, latest, trend, data["order_book_imbalance"])
    result["_indicators"] = latest  # برای محاسبه ریسک بعداً لازمه
    return result


def run_pipeline():
    print("🚀 شروع تحلیل بازار...")

    already_sent_today = count_signals_today()
    remaining_slots = MAX_DAILY_SIGNALS - already_sent_today
    if remaining_slots <= 0:
        print(f"✅ سقف {MAX_DAILY_SIGNALS} سیگنال امروز پر شده. توقف.")
        return

    exchange = get_exchange()
    scored_signals = []

    for symbol in COIN_LIST:
        result = analyze_symbol(exchange, symbol)
        if result and result["direction"] != "NONE":
            scored_signals.append(result)
            print(f"  {symbol}: {result['direction']} | امتیاز {result['score']}")

    top_signals = rank_and_filter_signals(scored_signals, MIN_SCORE_TO_SIGNAL, remaining_slots)

    if not top_signals:
        print("ℹ️ هیچ سیگنال با کیفیت کافی امروز پیدا نشد.")
        return

    print(f"\n✅ {len(top_signals)} سیگنال برتر پیدا شد. در حال تولید توضیح و ارسال...")

    for signal in top_signals:
        indicators = signal.pop("_indicators")
        risk_levels = calculate_risk_levels(indicators["close"], indicators["atr"], signal["direction"])
        if risk_levels is None:
            continue

        explanation = generate_explanation_safe(signal, risk_levels)
        send_telegram_message(explanation)
        save_signal_record(signal, risk_levels, explanation)
        print(f"  ✔️ سیگنال {signal['symbol']} ارسال و ذخیره شد.")

    print("\n🏁 اجرای پایپ‌لاین تمام شد.")


if __name__ == "__main__":
    run_pipeline()
