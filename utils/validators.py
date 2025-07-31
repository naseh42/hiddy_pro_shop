import re
from typing import Tuple

class Validators:
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """اعتبارسنجی شماره موبایل"""
        pattern = r'^09\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """اعتبارسنجی ایمیل"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """اعتبارسنجی نام کاربری"""
        if len(username) < 3 or len(username) > 30:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_amount(amount: float) -> Tuple[bool, str]:
        """اعتبارسنجی مبلغ"""
        if amount <= 0:
            return False, "مبلغ باید بیشتر از صفر باشد"
        if amount > 100000000:  # 100 میلیون تومان
            return False, "مبلغ بیش از حد مجاز"
        return True, ""
    
    @staticmethod
    def validate_iranian_bank_card(card_number: str) -> bool:
        """اعتبارسنجی شماره کارت بانکی ایرانی"""
        # حذف فاصله‌ها
        card_number = card_number.replace(" ", "")
        
        if len(card_number) != 16:
            return False
            
        if not card_number.isdigit():
            return False
            
        # الگوریتم Luhn
        def luhn_check(card_num):
            total = 0
            reverse_digits = card_num[::-1]
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n = n // 10 + n % 10
                total += n
            return total % 10 == 0
            
        return luhn_check(card_number)

# نمونه استفاده
# is_valid = Validators.validate_phone("09123456789")
