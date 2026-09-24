"""
Agent 1: Data Collector
دریافت داده‌ی OHLCV، حجم و Order Book از Binance (رایگان و بدون نیاز به API Key)
"""

import ccxt
import pandas as pd
import time
from config.settings import TIMEFRAME, HIGHER_TIMEFRAME, CANDLE_LIMIT


def get_exchange():
    """اتصال به Binance (فقط داده عمومی - نیازی به کلید نیست)"""
    return ccxt.binance({
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })


def fetch_ohlcv(exchange, symbol: str, timeframe: str = TIMEFRAME, limit: int = CANDLE_LIMIT) -> pd.DataFrame | None:
    """دریافت کندل‌ها و تبدیل به DataFrame"""
    try:
        raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not raw or len(raw) < 30:
            return None
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print(f"[WARN] خطا در دریافت {symbol}: {e}")
        return None


def fetch_order_book_imbalance(exchange, symbol: str) -> float | None:
    """
    نسبت حجم خرید به فروش در Order Book (سیگنال کوچک از فشار خرید/فروش لحظه‌ای)
    عدد بالاتر از ۱ یعنی فشار خرید بیشتره
    """
    try:
        ob = exchange.fetch_order_book(symbol, limit=20)
        bid_vol = sum([b[1] for b in ob["bids"]])
        ask_vol = sum([a[1] for a in ob["asks"]])
        if ask_vol == 0:
            return None
        return round(bid_vol / ask_vol, 3)
    except Exception:
        return None


def collect_symbol_data(exchange, symbol: str) -> dict | None:
    """جمع‌آوری همه‌ی داده‌های لازم برای یک نماد در یک دیکشنری"""
    df_main = fetch_ohlcv(exchange, symbol, TIMEFRAME)
    if df_main is None:
        return None

    df_higher = fetch_ohlcv(exchange, symbol, HIGHER_TIMEFRAME, limit=100)
    ob_imbalance = fetch_order_book_imbalance(exchange, symbol)

    return {
        "symbol": symbol,
        "df_main": df_main,
        "df_higher": df_higher,
        "order_book_imbalance": ob_imbalance,
        "current_price": float(df_main["close"].iloc[-1]),
    }


def collect_all_symbols(symbols: list[str]) -> dict:
    """جمع‌آوری داده برای کل لیست کوین‌ها - با تأخیر کوچیک برای رعایت Rate Limit"""
    exchange = get_exchange()
    results = {}
    for symbol in symbols:
        data = collect_symbol_data(exchange, symbol)
        if data:
            results[symbol] = data
        time.sleep(exchange.rateLimit / 1000)  # رعایت محدودیت نرخ Binance
    return results
