"""
ذخیره و خواندن تاریخچه سیگنال‌ها (فایل JSON ساده در خود ریپو - دیتابیس رایگان!)
این تاریخچه بعداً برای بک‌تست و ارزیابی دقت سیستم استفاده می‌شه.
"""

import json
import os
from datetime import datetime, timezone
from config.settings import HISTORY_FILE


def load_history() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_signal_record(signal: dict, risk_levels: dict, explanation: str) -> None:
    history = load_history()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": signal["symbol"],
        "direction": signal["direction"],
        "score": signal["score"],
        "reasons": signal["reasons"],
        "entry": risk_levels["entry"],
        "stop_loss": risk_levels["stop_loss"],
        "take_profit": risk_levels["take_profit"],
        "explanation": explanation,
        "outcome": "pending",  # بعداً با یک اسکریپت جداگانه ارزیابی می‌شه: win / loss / pending
    }
    history.append(record)

    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def count_signals_today() -> int:
    """برای رعایت محدودیت حداکثر ۱۰ سیگنال در روز"""
    history = load_history()
    today = datetime.now(timezone.utc).date().isoformat()
    return sum(1 for r in history if r["timestamp"].startswith(today))
