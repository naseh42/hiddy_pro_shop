import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import Config
from database import init_db, get_db
from utils.keyboards import Keyboards
from utils.helpers import Helpers
from modules.user_manager import UserManager
from modules.plan_manager import PlanManager
from modules.hidify_api import HiddifyAPI

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HiddyShopBot:
    def __init__(self):
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        self.hiddify_api = HiddifyAPI()
        self.setup_handlers()
    
    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        # دستورات اصلی
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("admin", self.admin_command))
        
        # کالبک‌های دکمه‌ها
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # پیام‌های متنی
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    async def start_command(self, update: Update, context):
        """دستور /start"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            # ایجاد کاربر در دیتابیس
            async for db in get_db():
                user_manager = UserManager(db)
                db_user = await user_manager.create_user(
                    telegram_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username
                )
                break
            
            # بررسی رفرال
            if context.args:
                referral_code = context.args[0]
                await self.handle_referral(user.id, referral_code)
            
            # ارسال منوی اصلی
            is_admin = user.id == Config.ADMIN_ID
            keyboard = Keyboards.main_menu(is_admin=is_admin)
            
            welcome_message = f"""
سلام {user.first_name} عزیز! 👋

به ربات فروشگاهی HiddyShop خوش آمدید.

از منوی زیر می‌توانید اقدامات مورد نظر خود را انجام دهید:
"""
            
            await update.message.reply_text(
                welcome_message,
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await update.message.reply_text("❌ خطایی رخ داده است!")
    
    async def help_command(self, update: Update, context):
        """دستور /help"""
        help_text = """
راهنمای استفاده از ربات:

🛍️ فروشگاه: مشاهده پلن‌های موجود و خرید
💳 کیف پول: مشاهده موجودی و افزایش اعتبار
👥 رفرال: دعوت دوستان و دریافت کمیسیون
📊 پروفایل: مشاهده اطلاعات کاربری

برای کمک بیشتر با پشتیبانی تماس بگیرید.
"""
        await update.message.reply_text(help_text)
    
    async def admin_command(self, update: Update, context):
        """دستور /admin"""
        user_id = update.effective_user.id
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text("❌ شما ادمین نیستید!")
            return
        
        keyboard = Keyboards.admin_menu()
        await update.message.reply_text(
            "پنل ادمین:",
            reply_markup=keyboard
        )
    
    async def button_handler(self, update: Update, context):
        """مدیریت کلیک دکمه‌ها"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        try:
            # منوی اصلی
            if data == "main_menu":
                is_admin = user_id == Config.ADMIN_ID
                keyboard = Keyboards.main_menu(is_admin=is_admin)
                await query.edit_message_text(
                    "منوی اصلی:",
                    reply_markup=keyboard
                )
            
            # فروشگاه
            elif data == "shop":
                await self.show_shop_menu(query)
            
            elif data == "plans_list":
                await self.show_plans_list(query)
            
            elif data.startswith("plan_"):
                plan_id = int(data.split("_")[1])
                await self.show_plan_details(query, plan_id)
            
            # کیف پول
            elif data == "wallet":
                await self.show_wallet_info(query)
            
            # رفرال
            elif data == "referral":
                await self.show_referral_info(query)
            
            # پروفایل
            elif data == "profile":
                await self.show_profile_info(query)
            
            # پنل ادمین
            elif data == "admin_panel":
                if user_id == Config.ADMIN_ID:
                    await self.show_admin_panel(query)
                else:
                    await query.answer("❌ دسترسی مجاز نیست!")
            
            # بخش‌های ادمین
            elif data == "admin_users":
                await self.show_admin_users(query)
            
            elif data == "admin_plans":
                await self.show_admin_plans(query)
            
            elif data == "admin_payments":
                await self.show_admin_payments(query)
            
            elif data == "admin_stats":
                await self.show_admin_stats(query)
            
            elif data == "admin_backup":
                await self.show_admin_backup(query)
            
            elif data == "admin_discount":
                await self.show_admin_discount(query)
            
            # عملیات پلن
            elif data.startswith("buy_plan_"):
                plan_id = int(data.split("_")[2])
                await self.buy_plan(query, plan_id)
            
            # بازگشت‌ها
            elif data == "back_to_shop":
                await self.show_shop_menu(query)
            
            elif data == "back_to_admin":
                await self.show_admin_panel(query)
            
            else:
                await query.answer("❌ گزینه نامعتبر!")
        
        except Exception as e:
            logger.error(f"Error in button_handler: {e}")
            await query.answer("❌ خطایی رخ داده است!")
    
    # توابع منوی اصلی
    async def show_shop_menu(self, query):
        """نمایش منوی فروشگاه"""
        keyboard = Keyboards.shop_menu()
        await query.edit_message_text(
            "🛍️ فروشگاه:\nلیست پلن‌های موجود:",
            reply_markup=keyboard
        )
    
    async def show_plans_list(self, query):
        """نمایش لیست پلن‌ها"""
        async for db in get_db():
            plan_manager = PlanManager(db)
            plans = await plan_manager.get_active_plans()
            break
        
        if not plans:
            await query.edit_message_text(
                "❌ هیچ پلنی موجود نیست!",
                reply_markup=Keyboards.back_to_main()
            )
            return
        
        keyboard = Keyboards.plans_list(plans)
        await query.edit_message_text(
            "📋 پلن‌های موجود:",
            reply_markup=keyboard
        )
    
    async def show_plan_details(self, query, plan_id):
        """نمایش جزئیات پلن"""
        async for db in get_db():
            plan_manager = PlanManager(db)
            plan = await plan_manager.get_plan_by_id(plan_id)
            break
        
        if not plan:
            await query.answer("❌ پلن یافت نشد!")
            return
        
        plan_info = f"""
📋 جزئیات پلن:

📝 نام: {plan.name}
⏱️ مدت زمان: {Helpers.format_days(plan.days)}
📊 ترافیک: {Helpers.format_traffic(plan.traffic_gb)}
💰 قیمت: {Helpers.format_price(plan.price)}

{plan.description or ''}
"""
        
        keyboard = Keyboards.plan_actions(plan_id)
        await query.edit_message_text(plan_info, reply_markup=keyboard)
    
    async def buy_plan(self, query, plan_id):
        """خرید پلن"""
        async for db in get_db():
            plan_manager = PlanManager(db)
            plan = await plan_manager.get_plan_by_id(plan_id)
            break
        
        if not plan:
            await query.answer("❌ پلن یافت نشد!")
            return
        
        buy_info = f"""
💳 خرید پلن: {plan.name}

💰 قیمت: {Helpers.format_price(plan.price)}
⏱️ مدت زمان: {Helpers.format_days(plan.days)}
📊 ترافیک: {Helpers.format_traffic(plan.traffic_gb)}

روش پرداخت خود را انتخاب کنید:
"""
        
        keyboard = Keyboards.payment_methods()
        await query.edit_message_text(buy_info, reply_markup=keyboard)
    
    async def show_wallet_info(self, query):
        """نمایش اطلاعات کیف پول"""
        user_id = query.from_user.id
        async for db in get_db():
            from modules.wallet import WalletManager
            wallet_manager = WalletManager(db)
            balance = await wallet_manager.get_user_wallet_balance(user_id)
            break
        
        wallet_info = f"""
💳 کیف پول شما:

💰 موجودی فعلی: {Helpers.format_price(balance)}

برای افزایش موجودی از طریق پنل ادمین اقدام کنید.
"""
        
        await query.edit_message_text(
            wallet_info,
            reply_markup=Keyboards.back_to_main()
        )
    
    async def show_referral_info(self, query):
        """نمایش اطلاعات رفرال - نسخه واقعی"""
        user_id = query.from_user.id
        
        try:
            async for db in get_db():
                from modules.user_manager import UserManager
                from modules.referral import ReferralManager
                
                user_manager = UserManager(db)
                referral_manager = ReferralManager(db)
                
                # دریافت اطلاعات کاربر
                user = await user_manager.get_user_by_telegram_id(user_id)
                if not user:
                    await query.answer("❌ خطا در دریافت اطلاعات کاربر!")
                    return
                
                # دریافت آمار رفرال
                stats = await referral_manager.get_user_referral_stats(user.id)
                
                # دریافت کاربران معرفی‌شده (آخرین 5 نفر)
                referred_users = await referral_manager.get_user_referrals(user.id, page=1, per_page=5)
                
                break
            
            # ساخت لیست کاربران معرفی‌شده
            referred_list = ""
            if referred_users:
                referred_list = "\nآخرین کاربران معرفی‌شده:\n"
                for i, (referred_user, created_at) in enumerate(referred_users, 1):
                    name = f"{referred_user.first_name or ''} {referred_user.last_name or ''}".strip()
                    if not name:
                        name = f"کاربر {referred_user.id}"
                    referred_list += f"{i}. {name} ({created_at.strftime('%Y/%m/%d')})\n"
            else:
                referred_list = "\nهنوز کاربری معرفی نکرده‌اید."
            
            referral_info = f"""
👥 برنامه رفرال:

🔗 کد رفرال شما: `{user.referral_code}`

📊 آمار:
├─ کاربران معرفی‌شده: {stats['referred_count']} نفر
├─ کمیسیون دریافت‌شده: {Helpers.format_price(stats['total_commission'])}
└─ کمیسیون در انتظار: {Helpers.format_price(stats['pending_commission'])}

💡 روش دعوت:
لینک دعوت شما:
`t.me/{(await self.app.bot.get_me()).username}?start={user.referral_code}`

{referred_list}

برای دعوت دوستان، لینک بالا را با آن‌ها به اشتراک بگذارید.
"""
            
            await query.edit_message_text(
                referral_info,
                reply_markup=Keyboards.back_to_main(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in show_referral_info: {e}")
            await query.answer("❌ خطایی رخ داده است!")
    
    async def show_profile_info(self, query):
        """نمایش اطلاعات پروفایل"""
        user = query.from_user
        user_id = user.id
        
        profile_info = f"""
📊 پروفایل کاربری:

👤 نام: {user.first_name} {user.last_name or ''}
🆔 آیدی تلگرام: {user.id}
📝 نام کاربری: @{user.username or 'ندارد'}

برای تغییر اطلاعات، از طریق تلگرام اقدام کنید.
"""
        
        await query.edit_message_text(
            profile_info,
            reply_markup=Keyboards.back_to_main()
        )
    
    # توابع پنل ادمین
    async def show_admin_panel(self, query):
        """نمایش پنل ادمین"""
        keyboard = Keyboards.admin_menu()
        await query.edit_message_text(
            "⚙️ پنل ادمین:",
            reply_markup=keyboard
        )
    
    async def show_admin_users(self, query):
        """نمایش مدیریت کاربران"""
        try:
            async for db in get_db():
                user_manager = UserManager(db)
                users = await user_manager.get_all_users(page=1, per_page=10)
                total_users = len(users)  # در نسخه واقعی باید از دیتابیس بگیریم
                break
            
            users_info = f"""
👥 مدیریت کاربران:

📊 آمار کلی:
├─ تعداد کل کاربران: {total_users}
├─ کاربران فعال: {len([u for u in users if u.is_active])}
└─ کاربران ادمین: {len([u for u in users if u.is_admin])}

عملیات موجود:
• مشاهده لیست کاربران
• مسدود/رفع مسدودی کاربران
• تغییر سطح دسترسی

این بخش در حال توسعه است.
"""
            
            keyboard = Keyboards.admin_back_menu()
            await query.edit_message_text(users_info, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error in show_admin_users: {e}")
            await query.answer("❌ خطایی رخ داده است!")
    
    async def show_admin_plans(self, query):
        """نمایش مدیریت پلن‌ها - نسخه واقعی"""
        try:
            async for db in get_db():
                plan_manager = PlanManager(db)
                plans = await plan_manager.get_all_plans(page=1, per_page=10)
                break
            
            if not plans:
                plans_text = "❌ هیچ پلنی تعریف نشده است."
            else:
                plans_text = "📋 لیست پلن‌های تعریف‌شده:\n\n"
                for i, plan in enumerate(plans, 1):
                    status = "فعال" if plan.is_active else "غیرفعال"
                    plans_text += f"{i}. {plan.name}\n"
                    plans_text += f"   ⏱️ {Helpers.format_days(plan.days)}\n"
                    plans_text += f"   📊 {Helpers.format_traffic(plan.traffic_gb)}\n"
                    plans_text += f"   💰 {Helpers.format_price(plan.price)}\n"
                    plans_text += f"   📊 وضعیت: {status}\n\n"
            
            plans_info = f"""
📋 مدیریت پلن‌ها:

{plans_text}

عملیات موجود:
• ایجاد پلن جدید
• ویرایش پلن‌های موجود
• فعال/غیرفعال کردن پلن‌ها
• حذف پلن‌ها
"""
            
            keyboard = Keyboards.admin_back_menu()
            await query.edit_message_text(plans_info, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error in show_admin_plans: {e}")
            await query.answer("❌ خطایی رخ داده است!")
    
    async def show_admin_payments(self, query):
        """نمایش مدیریت پرداخت‌ها"""
        admin_info = """
💰 مدیریت پرداخت‌ها:

در این بخش می‌توانید:
- لیست پرداخت‌ها را مشاهده کنید
- پرداخت‌های در انتظار تایید را بررسی کنید
- تراکنش‌ها را مدیریت کنید

این بخش در نسخه‌های بعدی پیاده‌سازی خواهد شد.
"""
        
        keyboard = Keyboards.admin_back_menu()
        await query.edit_message_text(admin_info, reply_markup=keyboard)
    
    async def show_admin_stats(self, query):
        """نمایش آمار سیستم"""
        admin_info = """
📊 آمار سیستم:

در این بخش می‌توانید:
- آمار کلی سیستم را مشاهده کنید
- گزارش‌های مالی را ببینید
- عملکرد ربات را بررسی کنید

این بخش در نسخه‌های بعدی پیاده‌سازی خواهد شد.
"""
        
        keyboard = Keyboards.admin_back_menu()
        await query.edit_message_text(admin_info, reply_markup=keyboard)
    
    async def show_admin_backup(self, query):
        """نمایش مدیریت بکاپ"""
        admin_info = """
💾 مدیریت بکاپ:

در این بخش می‌توانید:
- بکاپ از دیتابیس تهیه کنید
- بکاپ‌های قبلی را بازیابی کنید
- زمان‌بندی بکاپ خودکار تنظیم کنید

این بخش در نسخه‌های بعدی پیاده‌سازی خواهد شد.
"""
        
        keyboard = Keyboards.admin_back_menu()
        await query.edit_message_text(admin_info, reply_markup=keyboard)
    
    async def show_admin_discount(self, query):
        """نمایش مدیریت کدهای تخفیف"""
        admin_info = """
🏷️ مدیریت کدهای تخفیف:

در این بخش می‌توانید:
- کدهای تخفیف جدید ایجاد کنید
- کدهای موجود را مدیریت کنید
- آمار استفاده از کدها را ببینید

این بخش در نسخه‌های بعدی پیاده‌سازی خواهد شد.
"""
        
        keyboard = Keyboards.admin_back_menu()
        await query.edit_message_text(admin_info, reply_markup=keyboard)
    
    async def handle_referral(self, user_id: int, referral_code: str):
        """مدیریت رفرال"""
        try:
            async for db in get_db():
                from modules.user_manager import UserManager
                from modules.referral import ReferralManager
                
                user_manager = UserManager(db)
                referral_manager = ReferralManager(db)
                
                # پیدا کردن کاربر معرف
                referrer = await user_manager.get_user_by_referral_code(referral_code)
                if not referrer or referrer.telegram_id == user_id:
                    return
                
                # بررسی وجود رفرال قبلی
                existing_referral = await referral_manager.get_referral_by_users(
                    referrer.id, user_id
                )
                if existing_referral:
                    return
                
                # ایجاد رکورد رفرال
                await referral_manager.create_referral(
                    referrer_id=referrer.id,
                    referred_id=user_id
                )
                
                # اطلاع‌رسانی به کاربر معرف
                try:
                    await self.app.bot.send_message(
                        chat_id=referrer.telegram_id,
                        text=f"👥 کاربر جدید با کد رفرال شما ثبت‌نام کرد!"
                    )
                except:
                    pass  # اگر نتوانست پیام بفرستد، مهم نیست
                
                break
        except Exception as e:
            logger.error(f"Error in handle_referral: {e}")
    
    async def message_handler(self, update: Update, context):
        """مدیریت پیام‌های متنی"""
        await update.message.reply_text(
            "لطفاً از منوی اصلی استفاده کنید:",
            reply_markup=Keyboards.main_menu(
                is_admin=update.effective_user.id == Config.ADMIN_ID
            )
        )
    
    async def run(self):
        """اجرای ربات"""
        logger.info("ربات در حال اجراست...")
        await init_db()  # ایجاد دیتابیس
        await self.app.run_polling()

# اجرای ربات
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    
    bot = HiddyShopBot()
    import asyncio
    asyncio.run(bot.run())
