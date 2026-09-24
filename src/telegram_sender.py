"""
ارسال سیگنال نهایی به تلگرام از طریق Bot API (کاملاً رایگان)
"""

import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] تنظیمات تلگرام کامل نیست - پیام ارسال نشد")
        print("----- پیش‌نمایش پیام -----")
        print(text)
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}

    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] ارسال پیام تلگرام ناموفق بود: {e}")
        return False
