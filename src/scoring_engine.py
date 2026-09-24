"""
Agent 4 (Risk) + هسته‌ی امتیازدهی Agent 5 (Signal Composer)
منطق قطعی و ریاضی - هیچ LLM اینجا صدا زده نمی‌شه، فقط قوانین شفاف و قابل بک‌تست
"""

from config.settings import (
    RSI_OVERSOLD, RSI_OVERBOUGHT, RISK_REWARD_MIN, ATR_SL_MULTIPLIER,
)


def score_symbol(symbol: str, indicators: dict, trend: str, ob_imbalance: float | None) -> dict:
    """
    امتیازدهی یک نماد بر اساس ترکیب اندیکاتورها.
    خروجی: دیکشنری شامل جهت پیشنهادی (LONG/SHORT/NONE)، امتیاز ۰-۱۰۰، و دلایل.
    """
    score = 0
    reasons = []
    direction = None

    rsi = indicators.get("rsi")
    bb_percent = indicators.get("bb_percent")

    # ---------- تشخیص جهت اولیه بر اساس RSI + Bollinger ----------
    if rsi is not None and rsi < RSI_OVERSOLD:
        direction = "LONG"
        score += 25
        reasons.append(f"RSI در ناحیه اشباع فروش ({rsi})")
    elif rsi is not None and rsi > RSI_OVERBOUGHT:
        direction = "SHORT"
        score += 25
        reasons.append(f"RSI در ناحیه اشباع خرید ({rsi})")

    if bb_percent is not None:
        if bb_percent <= 0.05 and direction in (None, "LONG"):
            direction = "LONG"
            score += 15
            reasons.append("قیمت نزدیک باند پایین بولینگر")
        elif bb_percent >= 0.95 and direction in (None, "SHORT"):
            direction = "SHORT"
            score += 15
            reasons.append("قیمت نزدیک باند بالای بولینگر")

    if direction is None:
        return {"symbol": symbol, "direction": "NONE", "score": 0, "reasons": ["سیگنال واضحی یافت نشد"]}

    # ---------- تایید MACD ----------
    if direction == "LONG" and indicators.get("macd_bullish_cross"):
        score += 20
        reasons.append("کراس صعودی MACD")
    elif direction == "SHORT" and indicators.get("macd_bearish_cross"):
        score += 20
        reasons.append("کراس نزولی MACD")

    # ---------- تایید حجم ----------
    if indicators.get("volume_spike"):
        score += 15
        reasons.append("افزایش غیرعادی حجم معاملات")

    # ---------- تایید روند تایم‌فریم بالاتر (فیلتر مهم برای کاهش سیگنال کاذب) ----------
    if trend == "up" and direction == "LONG":
        score += 15
        reasons.append("هم‌راستا با روند صعودی تایم‌فریم بالاتر")
    elif trend == "down" and direction == "SHORT":
        score += 15
        reasons.append("هم‌راستا با روند نزولی تایم‌فریم بالاتر")
    elif trend != "unknown":
        score -= 20  # خلاف روند بزرگ‌تر - ریسک بالاتر
        reasons.append("⚠️ خلاف جهت روند تایم‌فریم بالاتر")

    # ---------- تایید Order Book ----------
    if ob_imbalance is not None:
        if direction == "LONG" and ob_imbalance > 1.2:
            score += 10
            reasons.append("فشار خرید بیشتر در Order Book")
        elif direction == "SHORT" and ob_imbalance < 0.8:
            score += 10
            reasons.append("فشار فروش بیشتر در Order Book")

    score = max(0, min(100, score))

    return {
        "symbol": symbol,
        "direction": direction,
        "score": score,
        "reasons": reasons,
    }


def calculate_risk_levels(entry_price: float, atr: float, direction: str) -> dict | None:
    """محاسبه حد ضرر و حد سود بر اساس ATR با رعایت حداقل نسبت ریسک به ریوارد"""
    if atr is None or atr <= 0:
        return None

    sl_distance = atr * ATR_SL_MULTIPLIER
    tp_distance = sl_distance * RISK_REWARD_MIN  # حداقل نسبت ۱.۵ به ۱

    if direction == "LONG":
        stop_loss = entry_price - sl_distance
        take_profit = entry_price + tp_distance
    elif direction == "SHORT":
        stop_loss = entry_price + sl_distance
        take_profit = entry_price - tp_distance
    else:
        return None

    return {
        "entry": round(entry_price, 8),
        "stop_loss": round(stop_loss, 8),
        "take_profit": round(take_profit, 8),
        "risk_reward_ratio": RISK_REWARD_MIN,
    }


def rank_and_filter_signals(scored_signals: list[dict], min_score: int, max_count: int) -> list[dict]:
    """فیلتر سیگنال‌های ضعیف و مرتب‌سازی بهترین‌ها - فقط N سیگنال برتر عبور می‌کنن"""
    qualified = [s for s in scored_signals if s["direction"] != "NONE" and s["score"] >= min_score]
    qualified.sort(key=lambda x: x["score"], reverse=True)
    return qualified[:max_count]
