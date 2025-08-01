from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    @staticmethod
    def main_menu(is_admin=False):
        """منوی اصلی"""
        buttons = [
            [InlineKeyboardButton("🛍️ فروشگاه", callback_data="shop")],
            [InlineKeyboardButton("💳 کیف پول", callback_data="wallet")],
            [InlineKeyboardButton("👥 رفرال", callback_data="referral")],
            [InlineKeyboardButton("📊 پروفایل", callback_data="profile")]
        ]
        
        # اضافه کردن گزینه درخواست نمایندگی برای همه کاربران
        buttons.append([InlineKeyboardButton("🏢 درخواست نمایندگی", callback_data="agent_request")])

        # اضافه کردن گزینه پنل ادمین فقط برای ادمین اصلی
        if is_admin:
            buttons.append([InlineKeyboardButton("⚙️ پنل ادمین", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def shop_menu():
        """منوی فروشگاه"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 لیست پلن‌ها", callback_data="plans_list")],
            [InlineKeyboardButton("🔍 جستجوی پلن", callback_data="search_plan")], # این هنوز پیاده نشده
            [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def admin_menu():
        """منوی ادمین"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")],
            [InlineKeyboardButton("📋 مدیریت پلن‌ها", callback_data="admin_plans")],
            [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
            [InlineKeyboardButton("🏢 درخواست‌های نمایندگی", callback_data="admin_agent_requests")],
            [InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats")],
            [InlineKeyboardButton("💾 مدیریت بکاپ", callback_data="admin_backup")],
            [InlineKeyboardButton("🏷️ کدهای تخفیف", callback_data="admin_discount")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def plans_list(plans):
        """لیست پلن‌های فعال"""
        buttons = []
        for plan in plans:
            button = InlineKeyboardButton(
                f"{plan.name} - {Helpers.format_price(plan.price)}", # فرمت قیمت
                callback_data=f"plan_{plan.id}"
            )
            buttons.append([button])
        
        buttons.append([InlineKeyboardButton("🏠 بازگشت", callback_data="shop")])
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def plan_actions(plan_id):
        """عملیات پلن (خرید)"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 خرید", callback_data=f"buy_plan_{plan_id}")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="plans_list")]
        ])
    
    @staticmethod
    def payment_methods():
        """روش‌های پرداخت"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 کیف پول", callback_data="pay_wallet")],
            [InlineKeyboardButton("💳 درگاه آنلاین", callback_data="pay_online")], # این هنوز پیاده نشده
            [InlineKeyboardButton("📱 کارت به کارت", callback_data="pay_manual")], # این هنوز پیاده نشده
            [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_payment():
        """تایید پرداخت (برای پرداخت‌های دستی)"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تایید پرداخت", callback_data="confirm_payment")],
            [InlineKeyboardButton("❌ لغو", callback_data="main_menu")]
        ])
    
    @staticmethod
    def back_to_main():
        """دکمه بازگشت به منوی اصلی"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ])
    
    @staticmethod
    def admin_back_menu():
        """دکمه‌های بازگشت در بخش ادمین"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 بازگشت به پنل ادمین", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")]
        ])
    
    # --- کیبوردهای مخصوص بخش مدیریت پلن‌ها (Admin Plans) ---
    @staticmethod
    def admin_plans_navigation(page: int, total_pages: int):
        """ناوبری صفحات پلن‌ها در پنل ادمین"""
        buttons = []
        
        # دکمه‌های صفحه‌بندی
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀ قبلی", callback_data=f"admin_plans_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("بعدی ▶", callback_data=f"admin_plans_page_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # دکمه ایجاد پلن جدید
        buttons.append([InlineKeyboardButton("➕ ایجاد پلن جدید", callback_data="create_plan")])
        
        # دکمه بازگشت
        buttons.append([InlineKeyboardButton("🏠 بازگشت", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def admin_back_to_plans():
        """بازگشت به مدیریت پلن‌ها"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 بازگشت به پلن‌ها", callback_data="admin_plans")],
            [InlineKeyboardButton("🏠 بازگشت به پنل ادمین", callback_data="admin_panel")]
        ])

    # --- کیبوردهای مخصوص بخش مدیریت کاربران (Admin Users) ---
    @staticmethod
    def admin_users_navigation(page: int, total_pages: int):
        """ناوبری صفحات کاربران در پنل ادمین"""
        buttons = []
        
        # دکمه‌های صفحه‌بندی
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀ قبلی", callback_data=f"admin_users_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("بعدی ▶", callback_data=f"admin_users_page_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # دکمه جستجو
        buttons.append([InlineKeyboardButton("🔍 جستجو کاربر", callback_data="search_user")]) # این هنوز پیاده نشده
        
        # دکمه بازگشت
        buttons.append([InlineKeyboardButton("🏠 بازگشت", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def admin_back_to_users():
        """بازگشت به مدیریت کاربران"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 بازگشت به کاربران", callback_data="admin_users")],
            [InlineKeyboardButton("🏠 بازگشت به پنل ادمین", callback_data="admin_panel")]
        ])

    # --- کیبوردهای مخصوص بخش مدیریت پرداخت‌ها (Admin Payments) ---
    @staticmethod
    def admin_payments_navigation(page: int, total_pages: int, status: str = "all"):
        """ناوبری صفحات پرداخت‌ها در پنل ادمین"""
        buttons = []
        
        # دکمه‌های فیلتر
        filter_buttons = [
            InlineKeyboardButton("همه", callback_data="admin_payments_all"),
            InlineKeyboardButton("در انتظار", callback_data="admin_payments_pending")
        ]
        buttons.append(filter_buttons)
        
        # دکمه‌های صفحه‌بندی
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀ قبلی", callback_data=f"admin_payments_page_{page-1}_{status}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("بعدی ▶", callback_data=f"admin_payments_page_{page+1}_{status}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # دکمه بازگشت
        buttons.append([InlineKeyboardButton("🏠 بازگشت", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def admin_back_to_payments():
        """بازگشت به مدیریت پرداخت‌ها"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 بازگشت به پرداخت‌ها", callback_data="admin_payments")],
            [InlineKeyboardButton("🏠 بازگشت به پنل ادمین", callback_data="admin_panel")]
        ])

    # --- کیبوردهای مخصوص بخش مدیریت کدهای تخفیف (Admin Discounts) ---
    @staticmethod
    def admin_discounts_navigation(page: int, total_pages: int):
        """ناوبری صفحات کدهای تخفیف در پنل ادمین"""
        buttons = []
        
        # دکمه‌های صفحه‌بندی
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀ قبلی", callback_data=f"admin_discounts_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("بعدی ▶", callback_data=f"admin_discounts_page_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # دکمه ایجاد کد تخفیف جدید
        buttons.append([InlineKeyboardButton("➕ ایجاد کد تخفیف", callback_data="create_discount")]) # این هنوز پیاده نشده
        
        # دکمه بازگشت
        buttons.append([InlineKeyboardButton("🏠 بازگشت", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def admin_back_to_discounts():
        """بازگشت به مدیریت کدهای تخفیف"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏷️ بازگشت به کدها", callback_data="admin_discount")],
            [InlineKeyboardButton("🏠 بازگشت به پنل ادمین", callback_data="admin_panel")]
        ])

    # --- کیبوردهای مخصوص بخش درخواست نمایندگی ---
    @staticmethod
    def confirm_agent_request():
        """تایید ارسال درخواست نمایندگی مجدد"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ارسال درخواست جدید", callback_data="submit_agent_request")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
        ])

# نکته: کلاس Helpers باید در utils/helpers.py تعریف شده باشد تا توابع فرمت‌بندی کار کنند.
# اگر نیست، باید از توابع ساده‌تر استفاده کنید یا کلاس Helpers را اضافه کنید.
# برای مثال:
# from utils.helpers import Helpers 
# باید در بالای این فایل ایمپورت شود یا توابع فرمت‌بندی را مستقیم در اینجا تعریف کنید.
# برای سادگی، من فرض می‌کنم Helpers در دسترس است. در غیر این صورت باید تغییر داده شود.
