from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.user_manager import UserManager
from utils.helpers import Helpers
from utils.keyboards import Keyboards

class UserAdmin:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_manager = UserManager(db)
    
    async def show_users_list(self, query, page: int = 1):
        """نمایش لیست کاربران برای ادمین"""
        per_page = 10
        users = await self.user_manager.get_all_users(page=page, per_page=per_page)
        total_users = await self.user_manager.get_users_count()
        total_pages = (total_users + per_page - 1) // per_page
        
        # دریافت آمار کلی
        active_users = await self.user_manager.get_active_users_count()
        admin_users = await self.user_manager.get_admin_users_count()
        blocked_users = await self.user_manager.get_blocked_users_count()
        
        if not users:
            users_text = "❌ هیچ کاربری ثبت نشده است."
        else:
            users_text = "👥 لیست کاربران:\n"
            for i, user in enumerate(users, 1):
                status = "فعال" if user.is_active else "غیرفعال"
                if user.is_blocked:
                    status = "مسدود"
                elif user.is_admin:
                    status = "ادمین"
                
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                if not name:
                    name = f"کاربر {user.telegram_id}"
                
                users_text += f"{i}. {name}\n"
                users_text += f"   🆔 {user.telegram_id}\n"
                users_text += f"   📊 وضعیت: {status}\n"
                users_text += f"   💰 کیف پول: {Helpers.format_price(user.wallet_balance)}\n"
                users_text += f"   🆔 /edit_user_{user.id}\n\n"
        
        users_info = f"""
👥 مدیریت کاربران:
صفحه {page} از {total_pages}
📊 آمار کلی:
├─ تعداد کل کاربران: {total_users}
├─ کاربران فعال: {active_users}
├─ کاربران ادمین: {admin_users}
├─ کاربران مسدود: {blocked_users}

{users_text}

عملیات موجود:
• مشاهده لیست کاربران
• مسدود/رفع مسدودی کاربران
• تغییر سطح دسترسی
• افزایش/کاهش کیف پول
"""
        
        keyboard = Keyboards.admin_users_navigation(page, total_pages)
        await query.edit_message_text(users_info, reply_markup=keyboard)
    
    async def show_user_details(self, query, user_id):
        """نمایش جزئیات کاربر"""
        user = await self.user_manager.get_user_by_id(user_id)
        if not user:
            await query.answer("❌ کاربر یافت نشد!")
            return
        
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not name:
            name = f"کاربر {user.telegram_id}"
        
        status = "فعال" if user.is_active else "غیرفعال"
        if user.is_blocked:
            status = "مسدود"
        elif user.is_admin:
            status = "ادمین"
        elif user.is_agent:
            status = "نماینده"
        
        user_info = f"""
👤 جزئیات کاربر: {name}
🆔 شناسه کاربری: {user.id}
🆔 آیدی تلگرام: {user.telegram_id}
📝 نام کاربری: @{user.username or 'ندارد'}
📞 شماره تلفن: {user.phone or 'ندارد'}
📊 وضعیت: {status}
💰 کیف پول: {Helpers.format_price(user.wallet_balance)}
🔗 کد رفرال: {user.referral_code}
📅 تاریخ عضویت: {user.created_at.strftime('%Y/%m/%d %H:%M')}

عملیات موجود:
/block_user_{user.id} - مسدود کردن کاربر
/unblock_user_{user.id} - رفع مسدودی کاربر
/set_admin_{user.id} - تغییر وضعیت ادمین
/set_agent_{user.id} - تغییر وضعیت نماینده
/add_wallet_{user.id} - افزایش کیف پول
/deduct_wallet_{user.id} - کسر از کیف پول
/delete_user_{user.id} - حذف کاربر
"""
        
        await query.edit_message_text(
            user_info,
            reply_markup=Keyboards.admin_back_to_users()
        )
        return f"viewing_user_{user_id}"
    
    async def toggle_user_block(self, query, user_id, block: bool):
        """مسدود/رفع مسدودی کاربر"""
        user = await self.user_manager.get_user_by_id(user_id)
        if not user:
            await query.answer("❌ کاربر یافت نشد!")
            return
        
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not name:
            name = f"کاربر {user.telegram_id}"
        
        if block:
            success = await self.user_manager.block_user(user_id)
            message = f"✅ کاربر '{name}' مسدود شد!"
        else:
            success = await self.user_manager.unblock_user(user_id)
            message = f"✅ کاربر '{name}' رفع مسدودی شد!"
        
        if success:
            await query.edit_message_text(
                message,
                reply_markup=Keyboards.admin_back_to_users()
            )
        else:
            await query.edit_message_text(
                "❌ خطا در تغییر وضعیت کاربر!",
                reply_markup=Keyboards.admin_back_to_users()
            )
    
    async def toggle_user_admin(self, query, user_id):
        """تغییر وضعیت ادمین کاربر"""
        user = await self.user_manager.get_user_by_id(user_id)
        if not user:
            await query.answer("❌ کاربر یافت نشد!")
            return
        
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not name:
            name = f"کاربر {user.telegram_id}"
        
        new_admin_status = not user.is_admin
        success = await self.user_manager.set_user_admin(user_id, new_admin_status)
        
        if success:
            status_text = "ادمین" if new_admin_status else "کاربر عادی"
            await query.edit_message_text(
                f"✅ کاربر '{name}' به '{status_text}' تغییر یافت!",
                reply_markup=Keyboards.admin_back_to_users()
            )
        else:
            await query.edit_message_text(
                "❌ خطا در تغییر سطح دسترسی کاربر!",
                reply_markup=Keyboards.admin_back_to_users()
            )
    
    async def toggle_user_agent(self, query, user_id):
        """تغییر وضعیت نماینده کاربر"""
        user = await self.user_manager.get_user_by_id(user_id)
        if not user:
            await query.answer("❌ کاربر یافت نشد!")
            return
        
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not name:
            name = f"کاربر {user.telegram_id}"
        
        new_agent_status = not user.is_agent
        success = await self.user_manager.set_user_agent(user_id, new_agent_status)
        
        if success:
            status_text = "نماینده" if new_agent_status else "کاربر عادی"
            await query.edit_message_text(
                f"✅ کاربر '{name}' به '{status_text}' تغییر یافت!",
                reply_markup=Keyboards.admin_back_to_users()
            )
        else:
            await query.edit_message_text(
                "❌ خطا در تغییر سطح دسترسی کاربر!",
                reply_markup=Keyboards.admin_back_to_users()
            )
    
    async def show_wallet_adjust_form(self, query, user_id, action: str):
        """نمایش فرم تنظیم کیف پول"""
        user = await self.user_manager.get_user_by_id(user_id)
        if not user:
            await query.answer("❌ کاربر یافت نشد!")
            return
        
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not name:
            name = f"کاربر {user.telegram_id}"
        
        action_text = "افزایش" if action == "add" else "کسر"
        
        form_text = f"""
💰 {action_text} کیف پول کاربر: {name}
شناسه کاربر: {user.id}
کیف پول فعلی: {Helpers.format_price(user.wallet_balance)}

لطفاً مبلغ {action_text} را به تومان وارد کنید:
مثال: 50000
"""
        
        await query.edit_message_text(
            form_text,
            reply_markup=Keyboards.admin_back_to_users()
        )
        return f"{action}_wallet_{user_id}"
    
    async def adjust_user_wallet(self, query, user_id, amount: float, action: str):
        """تنظیم کیف پول کاربر"""
        try:
            user = await self.user_manager.get_user_by_id(user_id)
            if not user:
                await query.edit_message_text(
                    "❌ کاربر یافت نشد!",
                    reply_markup=Keyboards.admin_back_to_users()
                )
                return
            
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            if not name:
                name = f"کاربر {user.telegram_id}"
            
            from modules.wallet import WalletManager
            wallet_manager = WalletManager(self.db)
            
            if action == "add":
                success = await wallet_manager.add_to_wallet(
                    user_id, 
                    amount, 
                    f"افزایش توسط ادمین"
                )
                action_text = "افزایش"
            else:
                success = await wallet_manager.deduct_from_wallet(
                    user_id, 
                    amount, 
                    f"کسر توسط ادمین"
                )
                action_text = "کسر"
            
            if success:
                new_balance = await wallet_manager.get_user_wallet_balance(user_id)
                await query.edit_message_text(
                    f"✅ {action_text} {Helpers.format_price(amount)} به کیف پول کاربر '{name}' انجام شد!\n"
                    f"💰 کیف پول فعلی: {Helpers.format_price(new_balance)}",
                    reply_markup=Keyboards.admin_back_to_users()
                )
            else:
                await query.edit_message_text(
                    "❌ خطا در تنظیم کیف پول کاربر!",
                    reply_markup=Keyboards.admin_back_to_users()
                )
        except Exception as e:
            await query.edit_message_text(
                f"❌ خطا در تنظیم کیف پول: {str(e)}",
                reply_markup=Keyboards.admin_back_to_users()
            )
    
    async def search_users_form(self, query):
        """نمایش فرم جستجوی کاربران"""
        form_text = """
🔍 جستجوی کاربران:
لطفاً نام، نام کاربری، آیدی تلگرام یا بخشی از اطلاعات کاربر را وارد کنید:
"""
        
        await query.edit_message_text(
            form_text,
            reply_markup=Keyboards.admin_back_to_users()
        )
        return "awaiting_user_search"
    
    async def search_users(self, query, search_query: str):
        """جستجوی کاربران"""
        try:
            users = await self.user_manager.search_users(search_query, page=1, per_page=20)
            
            if not users:
                await query.edit_message_text(
                    f"❌ کاربری با عبارت '{search_query}' یافت نشد!",
                    reply_markup=Keyboards.admin_back_to_users()
                )
                return
            
            users_text = f"👥 نتایج جستجو برای '{search_query}':\n\n"
            for i, user in enumerate(users, 1):
                status = "فعال" if user.is_active else "غیرفعال"
                if user.is_blocked:
                    status = "مسدود"
                elif user.is_admin:
                    status = "ادمین"
                
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                if not name:
                    name = f"کاربر {user.telegram_id}"
                
                users_text += f"{i}. {name}\n"
                users_text += f"   🆔 {user.telegram_id}\n"
                users_text += f"   📊 وضعیت: {status}\n"
                users_text += f"   💰 کیف پول: {Helpers.format_price(user.wallet_balance)}\n"
                users_text += f"   🆔 /edit_user_{user.id}\n\n"
            
            await query.edit_message_text(
                users_text,
                reply_markup=Keyboards.admin_back_to_users()
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ خطا در جستجو: {str(e)}",
                reply_markup=Keyboards.admin_back_to_users()
            )
