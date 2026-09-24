"""
تنظیمات مرکزی پروژه - لیست کوین‌ها، آستانه‌های سیگنال، و پارامترهای اندیکاتورها
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------- API Keys (از Environment Variables خونده می‌شه) ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ---------- تایم‌فریم تحلیل ----------
TIMEFRAME = "1h"          # کندل ساعتی برای تحلیل اصلی
HIGHER_TIMEFRAME = "4h"   # تایم‌فریم بالاتر برای تایید روند
CANDLE_LIMIT = 200        # تعداد کندل مورد نیاز برای محاسبه اندیکاتورها

# ---------- محدودیت سیگنال روزانه ----------
MAX_DAILY_SIGNALS = 10
MIN_SCORE_TO_SIGNAL = 75   # از ۱۰۰ - فقط سیگنال‌های خیلی قوی رد می‌شن

# ---------- لیست کوین‌ها (جفت‌ارز Binance) ----------
COIN_LIST = [
    "PEPE/USDT", "WIF/USDT", "SEI/USDT", "ACE/USDT", "DOGE/USDT",
    "SUI/USDT", "FET/USDT", "BOME/USDT", "FLOKI/USDT", "HOME/USDT",
    "BONK/USDT", "KAS/USDT", "ALLO/USDT", "SHIB/USDT", "ORDI/USDT",
    "TAO/USDT", "SOL/USDT", "XRP/USDT", "ARB/USDT", "XLM/USDT",
    "BTC/USDT", "ADA/USDT", "RENDER/USDT", "IMX/USDT", "GIGGLE/USDT",
    "AAVE/USDT", "ZRO/USDT", "HBAR/USDT", "LTC/USDT", "BCH/USDT",
    "JASMY/USDT", "JUP/USDT", "LAB/USDT", "TUT/USDT", "ETH/USDT",
    "HEI/USDT", "HMSTR/USDT", "ONDO/USDT", "KAITO/USDT", "BNB/USDT",
    "STX/USDT", "GRAM/USDT", "PYTH/USDT", "LDO/USDT", "LINK/USDT",
    "CAKE/USDT", "POL/USDT", "NOT/USDT", "ZEC/USDT", "DOT/USDT",
    "FIL/USDT", "BMT/USDT", "PUMP/USDT", "ATOM/USDT", "TIA/USDT",
    "TRX/USDT", "INJ/USDT", "UNI/USDT", "LUNC/USDT", "HEMI/USDT",
    "ICP/USDT", "PAXG/USDT", "XAUT/USDT", "HYPE/USDT", "APT/USDT",
    "ETHFI/USDT", "PROM/USDT", "ALGO/USDT", "AVAX/USDT", "WLD/USDT",
    "NEAR/USDT", "OP/USDT", "ENA/USDT",
]
# نکته: BRENTOIL/USDT از لیست حذف شد چون کامودیتی (نفت) است، نه کریپتو،
# و روی Binance Spot معمولی معامله نمی‌شود. اگر واقعاً نیاز است،
# باید صرافی/منبع داده جداگانه‌ای برایش تعریف شود.

# ---------- پارامترهای اندیکاتورها ----------
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD = 2

VOLUME_SPIKE_MULTIPLIER = 1.5  # حجم باید ۱.۵ برابر میانگین باشه تا "غیرعادی" حساب بشه

# ---------- مدیریت ریسک ----------
RISK_REWARD_MIN = 1.5   # حداقل نسبت ریسک به ریوارد قابل قبول
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.5  # فاصله حد ضرر بر اساس ATR

# ---------- مسیر ذخیره تاریخچه ----------
HISTORY_FILE = "history/signals_history.json"
