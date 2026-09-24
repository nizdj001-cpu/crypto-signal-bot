"""
Agent 2: Technical Analyst
محاسبه اندیکاتورهای تکنیکال با فرمول قطعی (بدون LLM) - سریع و قابل بک‌تست
"""

import pandas as pd
import ta
from config.settings import (
    RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, VOLUME_SPIKE_MULTIPLIER, ATR_PERIOD,
)


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """اضافه کردن ستون‌های اندیکاتور به DataFrame اصلی"""
    df = df.copy()

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=RSI_PERIOD).rsi()

    # MACD
    macd = ta.trend.MACD(df["close"], window_fast=MACD_FAST, window_slow=MACD_SLOW, window_sign=MACD_SIGNAL)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df["close"], window=BB_PERIOD, window_dev=BB_STD)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_percent"] = bb.bollinger_pband()  # موقعیت قیمت نسبت به باند (۰ تا ۱)

    # Volume
    df["volume_ma20"] = df["volume"].rolling(window=20).mean()
    df["volume_spike"] = df["volume"] > (df["volume_ma20"] * VOLUME_SPIKE_MULTIPLIER)

    # ATR (برای مدیریت ریسک / حد ضرر)
    df["atr"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], window=ATR_PERIOD).average_true_range()

    # EMA برای تشخیص روند کلی
    df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    df["ema200"] = ta.trend.EMAIndicator(df["close"], window=200).ema_indicator() if len(df) >= 200 else None

    return df


def get_trend_direction(df_higher: pd.DataFrame | None) -> str:
    """تشخیص روند در تایم‌فریم بالاتر (برای تایید جهت سیگنال)"""
    if df_higher is None or len(df_higher) < 50:
        return "unknown"
    df_higher = compute_indicators(df_higher)
    last = df_higher.iloc[-1]
    if pd.isna(last["ema50"]):
        return "unknown"
    return "up" if last["close"] > last["ema50"] else "down"


def summarize_latest(df: pd.DataFrame) -> dict:
    """خلاصه‌ی آخرین وضعیت اندیکاتورها برای استفاده در موتور امتیازدهی"""
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return {
        "rsi": round(last["rsi"], 2) if pd.notna(last["rsi"]) else None,
        "macd_diff": round(last["macd_diff"], 6) if pd.notna(last["macd_diff"]) else None,
        "macd_bullish_cross": bool(prev["macd_diff"] < 0 and last["macd_diff"] > 0),
        "macd_bearish_cross": bool(prev["macd_diff"] > 0 and last["macd_diff"] < 0),
        "bb_percent": round(last["bb_percent"], 3) if pd.notna(last["bb_percent"]) else None,
        "volume_spike": bool(last["volume_spike"]),
        "atr": round(last["atr"], 6) if pd.notna(last["atr"]) else None,
        "close": float(last["close"]),
        "above_ema50": bool(last["close"] > last["ema50"]) if pd.notna(last["ema50"]) else None,
    }
