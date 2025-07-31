#!/usr/bin/env python3
"""
نصاب حرفه‌ای ربات فروشگاهی HiddyShop
"""
import os
import sys
import json
from colorama import Fore, Style, init

# مقداردهی اولیه colorama
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}    🚀 نصاب حرفه‌ای ربات فروشگاهی HiddyShop")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}این اسکریپت تنظیمات مورد نیاز را از شما دریافت می‌کند")
    print(f"{Fore.CYAN}{'='*60}\n")

def get_input(prompt, required=True, default=None):
    """دریافت ورودی از کاربر"""
    while True:
        if default:
            user_input = input(f"{Fore.GREEN}{prompt} {Fore.YELLOW}[{default}]: {Fore.WHITE}")
            if not user_input and default:
                return default
            elif not user_input and required:
                print(f"{Fore.RED}❌ این فیلد الزامی است!")
                continue
            else:
                return user_input
        else:
            user_input = input(f"{Fore.GREEN}{prompt}: {Fore.WHITE}")
            if not user_input and required:
                print(f"{Fore.RED}❌ این فیلد الزامی است!")
                continue
            else:
                return user_input

def validate_url(url):
    """اعتبارسنجی URL"""
    return url.startswith(('http://', 'https://'))

def setup_hiddify():
    """دریافت تنظیمات هیدیفای"""
    print(f"{Fore.BLUE}🔧 تنظیمات پنل هیدیفای:")
    print(f"{Fore.MAGENTA}{'-'*40}")
    
    hiddify_base_url = ""
    while not validate_url(hiddify_base_url):
        hiddify_base_url = get_input("آدرس پنل هیدیفای (با http:// یا https://)")
        if not validate_url(hiddify_base_url):
            print(f"{Fore.RED}❌ آدرس نامعتبر است!")
    
    hiddify_api_key = get_input("API Key پنل هیدیفای")
    hiddify_proxy_path = get_input("مسیر پروکسی پنل", default="admin")
    hiddify_admin_uuid = get_input("UUID ادمین پنل")
    hiddify_admin_password = get_input("رمز عبور ادمین پنل")
    
    return {
        "HIDDIFY_BASE_URL": hiddify_base_url,
        "HIDDIFY_API_KEY": hiddify_api_key,
        "HIDDIFY_PROXY_PATH": hiddify_proxy_path,
        "HIDDIFY_ADMIN_UUID": hiddify_admin_uuid,
        "HIDDIFY_ADMIN_PASSWORD": hiddify_admin_password
    }

def setup_bot():
    """دریافت تنظیمات ربات"""
    print(f"\n{Fore.BLUE}🤖 تنظیمات ربات تلگرام:")
    print(f"{Fore.MAGENTA}{'-'*40}")
    
    bot_token = get_input("توکن ربات تلگرام")
    admin_id = get_input("آیدی عددی ادمین (آیدی تلگرام شما)")
    
    return {
        "BOT_TOKEN": bot_token,
        "ADMIN_ID": admin_id
    }

def setup_advanced():
    """تنظیمات پیشرفته"""
    print(f"\n{Fore.BLUE}⚙️ تنظیمات پیشرفته:")
    print(f"{Fore.MAGENTA}{'-'*40}")
    
    bot_name = get_input("نام ربات", default="HiddyShop Bot")
    
    return {
        "BOT_NAME": bot_name
    }

def create_env_file(config_data):
    """ایجاد فایل .env"""
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("# 🚀 تنظیمات ربات فروشگاهی HiddyShop\n")
            f.write("# تاریخ ایجاد: {}\n\n".format(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # هیدیفای
            f.write("# 🔧 تنظیمات پنل هیدیفای\n")
            f.write(f"HIDDIFY_BASE_URL={config_data['HIDDIFY_BASE_URL']}\n")
            f.write(f"HIDDIFY_API_KEY={config_data['HIDDIFY_API_KEY']}\n")
            f.write(f"HIDDIFY_PROXY_PATH={config_data['HIDDIFY_PROXY_PATH']}\n")
            f.write(f"HIDDIFY_ADMIN_UUID={config_data['HIDDIFY_ADMIN_UUID']}\n")
            f.write(f"HIDDIFY_ADMIN_PASSWORD={config_data['HIDDIFY_ADMIN_PASSWORD']}\n\n")
            
            # ربات
            f.write("# 🤖 تنظیمات ربات تلگرام\n")
            f.write(f"BOT_TOKEN={config_data['BOT_TOKEN']}\n")
            f.write(f"ADMIN_ID={config_data['ADMIN_ID']}\n\n")
            
            # پیشرفته
            f.write("# ⚙️ تنظیمات پیشرفته\n")
            f.write(f"BOT_NAME={config_data['BOT_NAME']}\n")
        
        print(f"\n{Fore.GREEN}✅ فایل .env با موفقیت ایجاد شد!")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ خطا در ایجاد فایل .env: {e}")
        return False

def install_requirements():
    """نصب وابستگی‌ها"""
    print(f"\n{Fore.YELLOW}📥 در حال نصب وابستگی‌ها...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ وابستگی‌ها با موفقیت نصب شدند!")
            return True
        else:
            print(f"{Fore.RED}❌ خطا در نصب وابستگی‌ها:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ خطا در نصب وابستگی‌ها: {e}")
        return False

def initialize_database():
    """ایجاد دیتابیس اولیه"""
    print(f"\n{Fore.YELLOW}💾 در حال ایجاد دیتابیس...")
    try:
        # اجرای اسکریپت ایجاد دیتابیس
        os.system(f"{sys.executable} -c \""
                  "import asyncio; "
                  "from database import init_db; "
                  "asyncio.run(init_db())"
                  "\"")
        print(f"{Fore.GREEN}✅ دیتابیس با موفقیت ایجاد شد!")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ خطا در ایجاد دیتابیس: {e}")
        return False

def show_completion_message():
    """نمایش پیام تکمیل"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}🎉 نصب با موفقیت انجام شد!")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"\n{Fore.BLUE}🚀 دستورات بعدی:")
    print(f"{Fore.WHITE}1. برای اجرای ربات: {Fore.YELLOW}python bot.py")
    print(f"{Fore.WHITE}2. برای اجرای با Docker: {Fore.YELLOW}docker-compose up -d")
    print(f"\n{Fore.MAGENTA}💡 نکته: مطمئن شوید پورت 8080 برای ربات آزاد است!")
    print(f"{Fore.MAGENTA}💡 برای تنظیمات پیشرفته‌تر از پنل ادمین استفاده کنید!")

def main():
    """تابع اصلی نصاب"""
    try:
        print_header()
        
        # دریافت تنظیمات
        hiddify_config = setup_hiddify()
        bot_config = setup_bot()
        advanced_config = setup_advanced()
        
        # ترکیب همه تنظیمات
        all_config = {
            **hiddify_config,
            **bot_config,
            **advanced_config
        }
        
        # ایجاد فایل .env
        if not create_env_file(all_config):
            print(f"{Fore.RED}❌ نصب ناقص بود!")
            return False
            
        # نصب وابستگی‌ها
        if not install_requirements():
            print(f"{Fore.RED}❌ نصب وابستگی‌ها ناقص بود!")
            return False
            
        # ایجاد دیتابیس
        if not initialize_database():
            print(f"{Fore.RED}❌ ایجاد دیتابیس ناقص بود!")
            return False
            
        # نمایش پیام تکمیل
        show_completion_message()
        return True
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 نصب لغو شد!")
        return False
    except Exception as e:
        print(f"\n{Fore.RED}❌ خطای ناگهانی: {e}")
        return False

if __name__ == "__main__":
    main()
