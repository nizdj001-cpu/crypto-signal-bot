"""
Agent 5: Signal Composer (سرپرست تیم)
اینجا تنها جایی هست که LLM (از طریق Groq رایگان) صدا زده می‌شه -
فقط برای سیگنال‌های نهایی که از فیلتر امتیازدهی قطعی عبور کردن (حداکثر ۱۰ بار در روز)
"""

from crewai import Agent, Task, Crew, LLM
from config.settings import GROQ_API_KEY


def get_groq_llm():
    """اتصال به Groq (رایگان) به‌جای مدل‌های پولی"""
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.3,  # پایین نگه داشتن دما برای خروجی دقیق‌تر و کمتر خلاقانه
    )


def build_signal_composer_agent() -> Agent:
    return Agent(
        role="تحلیل‌گر ارشد سیگنال کریپتو",
        goal="تبدیل داده‌های خام تکنیکال به یک توضیح کوتاه، دقیق و قابل‌فهم برای معامله‌گر",
        backstory=(
            "تو یک تحلیل‌گر باتجربه بازار کریپتو هستی که وظیفه‌ات نوشتن خلاصه‌ی نهایی سیگنال‌هاست. "
            "تو هرگز عدد یا دلیل جدید اختراع نمی‌کنی - فقط داده‌هایی که بهت داده می‌شه رو "
            "به زبان ساده و حرفه‌ای برای معامله‌گر توضیح می‌دی. همیشه ریسک رو هم یادآوری می‌کنی."
        ),
        llm=get_groq_llm(),
        verbose=False,
    )


def generate_signal_explanation(signal: dict, risk_levels: dict) -> str:
    """
    تولید توضیح نهایی برای یک سیگنال با استفاده از Agent.
    ورودی: دیکشنری امتیاز/دلایل از scoring_engine + سطوح ریسک
    """
    agent = build_signal_composer_agent()

    prompt = f"""
داده‌های سیگنال زیر رو به یک پیام کوتاه فارسی (حداکثر ۴ خط) برای ارسال به تلگرام تبدیل کن.
فقط از داده‌های زیر استفاده کن، هیچ عدد یا ادعای جدیدی اضافه نکن:

نماد: {signal['symbol']}
جهت: {signal['direction']}
امتیاز اطمینان: {signal['score']} از ۱۰۰
دلایل فنی: {', '.join(signal['reasons'])}
قیمت ورود: {risk_levels['entry']}
حد ضرر: {risk_levels['stop_loss']}
حد سود: {risk_levels['take_profit']}

فرمت خروجی: مستقیم پیام رو بنویس، بدون مقدمه یا توضیح اضافه، به فارسی روان.
"""

    task = Task(
        description=prompt,
        expected_output="یک پیام کوتاه فارسی آماده ارسال به تلگرام",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    return str(result)


def generate_explanation_safe(signal: dict, risk_levels: dict) -> str:
    """
    نسخه‌ی امن: اگه Groq در دسترس نبود یا خطا داد، یک پیام fallback قطعی (بدون AI) می‌سازه
    تا کل سیستم متوقف نشه.
    """
    try:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY تنظیم نشده")
        return generate_signal_explanation(signal, risk_levels)
    except Exception as e:
        print(f"[WARN] تولید توضیح با LLM ناموفق بود ({e})، از قالب پیش‌فرض استفاده می‌شه")
        reasons_text = "، ".join(signal["reasons"])
        return (
            f"📊 سیگنال {signal['direction']} برای {signal['symbol']}\n"
            f"امتیاز اطمینان: {signal['score']}/100\n"
            f"دلایل: {reasons_text}\n"
            f"ورود: {risk_levels['entry']} | حد ضرر: {risk_levels['stop_loss']} | حد سود: {risk_levels['take_profit']}\n"
            f"⚠️ این سیگنال توصیه مالی نیست، مدیریت ریسک با خودتونه."
        )
