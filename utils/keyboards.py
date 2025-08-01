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
        
        if is_admin:
            buttons.append([InlineKeyboardButton("⚙️ پنل ادمین", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def shop_menu():
        """منوی فروشگاه"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 لیست پلن‌ها", callback_data="plans_list")],
            [InlineKeyboardButton("🔍 جستجوی پلن", callback_data="search_plan")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def admin_menu():
        """منوی ادمین"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")],
            [InlineKeyboardButton("📋 مدیریت پلن‌ها", callback_data="admin_plans")],
            [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
            [InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats")],
            [InlineKeyboardButton("💾 مدیریت بکاپ", callback_data="admin_backup")],
            [InlineKeyboardButton("🏷️ کدهای تخفیف", callback_data="admin_discount")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def plans_list(plans):
        """لیست پلن‌ها"""
        buttons = []
        for plan in plans:
            button = InlineKeyboardButton(
                f"{plan.name} - {plan.price} تومان",
                callback_data=f"plan_{plan.id}"
            )
            buttons.append([button])
        
        buttons.append([InlineKeyboardButton("🏠 بازگشت", callback_data="shop")])
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def plan_actions(plan_id):
        """عملیات پلن"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 خرید", callback_data=f"buy_plan_{plan_id}")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="plans_list")]
        ])
    
    @staticmethod
    def payment_methods():
        """روش‌های پرداخت"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 کیف پول", callback_data="pay_wallet")],
            [InlineKeyboardButton("💳 درگاه آنلاین", callback_data="pay_online")],
            [InlineKeyboardButton("📱 کارت به کارت", callback_data="pay_manual")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_payment():
        """تایید پرداخت"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تایید پرداخت", callback_data="confirm_payment")],
            [InlineKeyboardButton("❌ لغو", callback_data="main_menu")]
        ])
    
    @staticmethod
    def back_to_main():
        """بازگشت به منوی اصلی"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ])
    
    @staticmethod
    def admin_back_menu():
        """منوی بازگشت برای بخش‌های ادمین"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 بازگشت به پنل ادمین", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")]
        ])
    
    @staticmethod
    def user_management_menu():
        """منوی مدیریت کاربران"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 لیست کاربران", callback_data="list_users")],
            [InlineKeyboardButton("➕ ایجاد کاربر", callback_data="create_user")],
            [InlineKeyboardButton("🔍 جستجو کاربر", callback_data="search_user")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="admin_panel")]
        ])
    
    @staticmethod
    def plan_management_menu():
        """منوی مدیریت پلن‌ها"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 لیست پلن‌ها", callback_data="list_plans_admin")],
            [InlineKeyboardButton("➕ ایجاد پلن", callback_data="create_plan")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="admin_panel")]
        ])
    
    @staticmethod
    def admin_plans_navigation(page: int, total_pages: int):
        """ناوبری صفحات پلن‌ها"""
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
    
    @staticmethod
    def admin_users_navigation(page: int, total_pages: int):
        """ناوبری صفحات کاربران"""
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
        buttons.append([InlineKeyboardButton("🔍 جستجو کاربر", callback_data="search_user")])
        
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

# نمونه استفاده
# keyboard = Keyboards.main_menu(is_admin=True)
