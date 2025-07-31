import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Optional

class Helpers:
    @staticmethod
    def generate_referral_code(length=8):
        """تولید کد رفرال منحصر به فرد"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_uuid():
        """تولید UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def format_price(price: float) -> str:
        """فرمت قیمت به صورت خوانا"""
        return f"{int(price):,} تومان"
    
    @staticmethod
    def format_traffic(traffic_gb: float) -> str:
        """فرمت ترافیک"""
        if traffic_gb >= 1024:
            return f"{traffic_gb/1024:.1f} TB"
        return f"{traffic_gb} GB"
    
    @staticmethod
    def format_days(days: int) -> str:
        """فرمت تعداد روزها"""
        if days >= 365:
            years = days // 365
            remaining_days = days % 365
            if remaining_days > 0:
                return f"{years} سال و {remaining_days} روز"
            return f"{years} سال"
        elif days >= 30:
            months = days // 30
            remaining_days = days % 30
            if remaining_days > 0:
                return f"{months} ماه و {remaining_days} روز"
            return f"{months} ماه"
        return f"{days} روز"
    
    @staticmethod
    def calculate_expiry_date(days: int) -> datetime:
        """محاسبه تاریخ انقضا"""
        return datetime.now() + timedelta(days=days)
    
    @staticmethod
    def is_expired(expiry_date: datetime) -> bool:
        """بررسی انقضای سرویس"""
        return datetime.now() > expiry_date

# نمونه استفاده
# code = Helpers.generate_referral_code()
# formatted_price = Helpers.format_price(50000)
