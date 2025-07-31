import os
from dotenv import load_dotenv

# بارگذاری تنظیمات از فایل .env
load_dotenv()

class Config:
    # تنظیمات هیدیفای
    HIDDIFY_BASE_URL = os.getenv("HIDDIFY_BASE_URL", "http://localhost:8080")
    HIDDIFY_API_KEY = os.getenv("HIDDIFY_API_KEY")
    HIDDIFY_PROXY_PATH = os.getenv("HIDDIFY_PROXY_PATH", "admin")
    HIDDIFY_ADMIN_UUID = os.getenv("HIDDIFY_ADMIN_UUID")
    HIDDIFY_ADMIN_PASSWORD = os.getenv("HIDDIFY_ADMIN_PASSWORD")
    
    # تنظیمات ربات
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # تنظیمات دیتابیس
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./hiddyshop.db")
    
    # تنظیمات ربات
    BOT_NAME = os.getenv("BOT_NAME", "HiddyShop Bot")
