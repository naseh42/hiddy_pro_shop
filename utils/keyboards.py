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

# نمونه استفاده
# keyboard = Keyboards.main_menu(is_admin=True)
