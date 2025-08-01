#!/bin/bash

# اسکریپت نصب ربات فروشگاهی HiddyShop
# نویسنده: آسانسور فارسی 🤖

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# تابع پاک کردن صفحه
clear_screen() {
    clear
}

# هدر
print_header() {
    clear_screen
    echo -e "${CYAN}==================================================${NC}"
    echo -e "${GREEN}    🚀 اسکریپت نصب ربات فروشگاهی HiddyShop${NC}"
    echo -e "${CYAN}==================================================${NC}"
    echo -e "${YELLOW}این اسکریپت تمام مراحل نصب را به صورت خودکار انجام می‌دهد${NC}"
    echo -e "${CYAN}==================================================${NC}"
    echo ""
}

# بررسی پیش‌نیازها
check_prerequisites() {
    echo -e "${BLUE}🔍 بررسی پیش‌نیازها...${NC}"
    
    # بررسی پایتون
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ پایتون 3 پیدا نشد!${NC}"
        echo -e "${YELLOW}لطفاً ابتدا پایتون 3 را نصب کنید.${NC}"
        exit 1
    fi
    
    # بررسی pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}⚠️  pip3 پیدا نشد، در حال نصب...${NC}"
        sudo apt update
        sudo apt install python3-pip -y
    fi
    
    # بررسی git
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}⚠️  git پیدا نشد، در حال نصب...${NC}"
        sudo apt install git -y
    fi
    
    echo -e "${GREEN}✅ پیش‌نیازها بررسی شدند${NC}"
}

# نصب وابستگی‌ها
install_dependencies() {
    echo -e "${BLUE}📥 در حال نصب وابستگی‌ها...${NC}"
    
    if pip3 install -r requirements.txt; then
        echo -e "${GREEN}✅ وابستگی‌ها نصب شدند${NC}"
    else
        echo -e "${RED}❌ خطا در نصب وابستگی‌ها${NC}"
        exit 1
    fi
}

# اجرای نصاب پایتونی
run_setup() {
    echo -e "${BLUE}🔧 در حال اجرای نصاب...${NC}"
    
    if python3 setup.py; then
        echo -e "${GREEN}✅ نصاب با موفقیت اجرا شد${NC}"
    else
        echo -e "${RED}❌ خطا در اجرای نصاب${NC}"
        exit 1
    fi
}

# ایجاد دایرکتوری‌های مورد نیاز
create_directories() {
    echo -e "${BLUE}📁 در حال ایجاد دایرکتوری‌ها...${NC}"
    mkdir -p data logs
    echo -e "${GREEN}✅ دایرکتوری‌ها ایجاد شدند${NC}"
}

# نمایش راهنمای اجرا
show_usage() {
    echo -e "\n${CYAN}==================================================${NC}"
    echo -e "${GREEN}🎉 نصب با موفقیت انجام شد!${NC}"
    echo -e "${CYAN}==================================================${NC}"
    echo -e "${BLUE}🚀 دستورات بعدی:${NC}"
    echo -e "${WHITE}1. برای اجرای ربات: ${YELLOW}python3 bot.py${NC}"
    echo -e "${WHITE}2. برای اجرای با Docker: ${YELLOW}docker-compose up -d${NC}"
    echo -e "${WHITE}3. برای مشاهده لاگ‌ها: ${YELLOW}tail -f logs/bot.log${NC}"
    echo -e "\n${MAGENTA}💡 نکته: مطمئن شوید پورت 8080 برای ربات آزاد است!${NC}"
    echo -e "${MAGENTA}💡 برای تنظیمات پیشرفته‌تر از پنل ادمین استفاده کنید!${NC}"
}

# تابع اصلی
main() {
    print_header
    check_prerequisites
    create_directories
    install_dependencies
    run_setup
    show_usage
}

# اجرای اسکریپت
main "$@"
