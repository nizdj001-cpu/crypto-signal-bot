# 🤖 Crypto Signal Bot

سیستم سیگنال‌دهی خودکار ارز دیجیتال با هزینه‌ی صفر — تحلیل تکنیکال قطعی + توضیح نهایی با LLM رایگان.

## ⚠️ هشدار مهم
این ابزار **توصیه مالی نیست**. سیگنال‌ها بر اساس تحلیل تکنیکال تولید می‌شن و هیچ تضمینی برای سودآوری وجود نداره. مدیریت ریسک و تصمیم نهایی همیشه با خود معامله‌گره.

## 🏗️ معماری

```
Binance API (رایگان) → محاسبه اندیکاتورها (RSI, MACD, BB, Volume)
        ↓
موتور امتیازدهی قطعی (بدون AI) → فیلتر فقط سیگنال‌های قوی (حداکثر ۱۰ در روز)
        ↓
Agent نهایی (Groq LLM رایگان) → تولید توضیح خوانا
        ↓
ارسال به تلگرام + ذخیره در history/signals_history.json
```

## 📋 پیش‌نیازها (همه رایگان)

1. حساب [Groq](https://console.groq.com) برای گرفتن `GROQ_API_KEY`
2. یک ربات تلگرام از [@BotFather](https://t.me/BotFather) برای گرفتن `TELEGRAM_BOT_TOKEN`
3. Chat ID خودتون در تلگرام (از [@userinfobot](https://t.me/userinfobot) بگیرید) برای `TELEGRAM_CHAT_ID`

## 🚀 راه‌اندازی

### ۱. تست لوکال (اختیاری)
```bash
git clone <your-repo-url>
cd crypto-signal-bot
pip install -r requirements.txt
cp .env.example .env
# مقادیر .env رو پر کنید
python main.py
```

### ۲. راه‌اندازی خودکار روی GitHub (اصلی)
1. این ریپو رو در گیت‌هاب خودتون Fork/Push کنید
2. برید به: `Settings → Secrets and variables → Actions → New repository secret`
3. سه Secret زیر رو اضافه کنید:
   - `GROQ_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. تب `Actions` رو باز کنید و Workflow رو فعال کنید (ممکنه نیاز به تایید اولیه باشه)
5. تمام! از این به بعد هر ۱۵ دقیقه به‌صورت خودکار اجرا می‌شه.

می‌تونید از تب Actions هم به‌صورت دستی (`Run workflow`) تستش کنید.

## 📁 ساختار پروژه

```
crypto-signal-bot/
├── .github/workflows/signal_bot.yml   # زمان‌بندی اجرای خودکار
├── config/settings.py                 # تنظیمات، لیست کوین‌ها، آستانه‌ها
├── src/
│   ├── data_collector.py     # Agent 1: دریافت داده از Binance
│   ├── indicators.py         # Agent 2: محاسبه اندیکاتورهای تکنیکال
│   ├── scoring_engine.py     # Agent 4: امتیازدهی و مدیریت ریسک
│   ├── crew_agents.py        # Agent 5: تولید توضیح نهایی با CrewAI + Groq
│   ├── telegram_sender.py    # ارسال پیام به تلگرام
│   └── storage.py            # ذخیره تاریخچه سیگنال‌ها
├── history/signals_history.json       # تاریخچه سیگنال‌ها (برای بک‌تست بعدی)
├── main.py                            # نقطه ورود اصلی
└── requirements.txt
```

## ⚙️ تنظیمات قابل تغییر (در `config/settings.py`)

| پارامتر | توضیح | مقدار پیش‌فرض |
|---|---|---|
| `MAX_DAILY_SIGNALS` | حداکثر سیگنال در روز | ۱۰ |
| `MIN_SCORE_TO_SIGNAL` | حداقل امتیاز برای صدور سیگنال (از ۱۰۰) | ۷۵ |
| `TIMEFRAME` | تایم‌فریم اصلی تحلیل | 1h |
| `RISK_REWARD_MIN` | حداقل نسبت ریسک به ریوارد | 1.5 |

## 🔜 قدم‌های بعدی پیشنهادی
- افزودن ماژول ارزیابی خودکار نتیجه سیگنال‌های قبلی (win/loss) برای محاسبه دقت واقعی سیستم
- افزودن داده‌ی سنتیمنت (اخبار، Fear & Greed Index)
- ساخت داشبورد وب ساده روی GitHub Pages برای نمایش تاریخچه و آمار عملکرد
