from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.payment_manager import PaymentManager
from modules.user_manager import UserManager
from utils.helpers import Helpers
from utils.keyboards import Keyboards

class PaymentAdmin:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_manager = PaymentManager(db)
        self.user_manager = UserManager(db)
    
    async def show_payments_list(self, query, page: int = 1, status: str = "all"):
        """نمایش لیست پرداخت‌ها برای ادمین"""
        per_page = 10
        if status == "all":
            # دریافت آمار کلی
            total_payments = await self.payment_manager.get_payments_count()
            success_payments = await self.payment_manager.get_success_payments_count()
            failed_payments = await self.payment_manager.get_failed_payments_count()
            pending_payments = await self.payment_manager.get_pending_payments_count()
        elif status == "pending":
            payments = await self.payment_manager.get_pending_payments(page=page, per_page=per_page)
            total_payments = await self.payment_manager.get_pending_payments_count()
        else:
            # برای سایر وضعیت‌ها
            pass
        
        total_pages = (total_payments + per_page - 1) // per_page
        
        if status == "all":
            payments_text = "📊 آمار کلی پرداخت‌ها:\n"
            payments_text += f"├─ تعداد کل پرداخت‌ها: {total_payments}\n"
            payments_text += f"├─ پرداخت‌های موفق: {success_payments}\n"
            payments_text += f"├─ پرداخت‌های ناموفق: {failed_payments}\n"
            payments_text += f"└─ پرداخت‌های در انتظار: {pending_payments}\n\n"
            
            payments_text += "📋 آخرین پرداخت‌ها:\n"
        else:
            payments_text = f"📋 پرداخت‌های {self._get_status_persian(status)}:\n"
        
        if status == "pending":
            payments = await self.payment_manager.get_pending_payments(page=page, per_page=per_page)
        else:
            # دریافت آخرین پرداخت‌ها
            from models.payment import Payment
            offset = (page - 1) * per_page
            result = await self.db.execute(
                select(Payment)
                .order_by(Payment.created_at.desc())
                .offset(offset).limit(per_page)
            )
            payments = result.scalars().all()
        
        if not payments:
            payments_text += "❌ هیچ پرداختی ثبت نشده است."
        else:
            for i, payment in enumerate(payments, 1):
                user = await self.user_manager.get_user_by_id(payment.user_id)
                user_name = "ناشناس"
                if user:
                    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                    if name:
                        user_name = name
                    else:
                        user_name = f"کاربر {user.telegram_id}"
                
                status_text = self._get_status_persian(payment.status)
                method_text = self._get_method_persian(payment.payment_method)
                
                payments_text += f"{i}. {user_name}\n"
                payments_text += f"   💰 {Helpers.format_price(payment.amount)}\n"
                payments_text += f"   📊 روش: {method_text}\n"
                payments_text += f"   📊 وضعیت: {status_text}\n"
                payments_text += f"   📅 {payment.created_at.strftime('%Y/%m/%d %H:%M')}\n"
                if payment.status == "pending":
                    payments_text += f"   🆔 /verify_payment_{payment.id}\n"
                payments_text += "\n"
        
        payments_info = f"""
💰 مدیریت پرداخت‌ها:
صفحه {page} از {total_pages}

{payments_text}

عملیات موجود:
• مشاهده پرداخت‌های در انتظار تایید
• تایید/رد پرداخت‌های دستی
• مشاهده آمار کلی پرداخت‌ها
"""
        
        keyboard = Keyboards.admin_payments_navigation(page, total_pages, status)
        await query.edit_message_text(payments_info, reply_markup=keyboard)
    
    async def show_pending_payments(self, query, page: int = 1):
        """نمایش پرداخت‌های در انتظار تایید"""
        await self.show_payments_list(query, page, "pending")
    
    async def show_payment_details(self, query, payment_id):
        """نمایش جزئیات پرداخت"""
        from models.payment import Payment
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            await query.answer("❌ پرداخت یافت نشد!")
            return
        
        user = await self.user_manager.get_user_by_id(payment.user_id)
        user_name = "ناشناس"
        if user:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            if name:
                user_name = name
            else:
                user_name = f"کاربر {user.telegram_id}"
        
        status_text = self._get_status_persian(payment.status)
        method_text = self._get_method_persian(payment.payment_method)
        
        payment_info = f"""
💳 جزئیات پرداخت:
🆔 شناسه پرداخت: {payment.id}
👤 کاربر: {user_name}
💰 مبلغ: {Helpers.format_price(payment.amount)}
💱 ارز: {payment.currency}
📊 روش پرداخت: {method_text}
🏪 درگاه: {payment.payment_gateway or 'ندارد'}
📊 وضعیت: {status_text}
📝 توضیحات: {payment.description or 'ندارد'}
📅 تاریخ ایجاد: {payment.created_at.strftime('%Y/%m/%d %H:%M')}
📅 تاریخ بروزرسانی: {payment.updated_at.strftime('%Y/%m/%d %H:%M')}
🆔 شناسه تراکنش: {payment.transaction_id or 'ندارد'}
🆔 authority: {payment.authority or 'ندارد'}

عملیات موجود:
"""
        
        buttons = []
        if payment.status == "pending":
            buttons.append([
                InlineKeyboardButton("✅ تایید پرداخت", callback_data=f"verify_payment_{payment.id}_success"),
                InlineKeyboardButton("❌ رد پرداخت", callback_data=f"verify_payment_{payment.id}_failed")
            ])
        
        buttons.append([InlineKeyboardButton("🏠 بازگشت", callback_data="admin_payments")])
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(payment_info, reply_markup=keyboard)
    
    async def verify_payment(self, query, payment_id, is_success: bool):
        """تایید یا رد پرداخت"""
        from models.payment import Payment
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            await query.answer("❌ پرداخت یافت نشد!")
            return
        
        if payment.status != "pending":
            await query.answer("❌ این پرداخت قابل تایید نیست!")
            return
        
        status = "success" if is_success else "failed"
        success = await self.payment_manager.update_payment_status(payment_id, status)
        
        if success:
            action_text = "تایید" if is_success else "رد"
            await query.edit_message_text(
                f"✅ پرداخت با موفقیت {action_text} شد!",
                reply_markup=Keyboards.admin_back_to_payments()
            )
            
            # اگر پرداخت تایید شد، موجودی کیف پول را افزایش دهیم
            if is_success:
                from modules.wallet import WalletManager
                wallet_manager = WalletManager(self.db)
                await wallet_manager.add_to_wallet(
                    payment.user_id,
                    payment.amount,
                    f"شارژ کیف پول از طریق پرداخت #{payment.id}"
                )
        else:
            await query.edit_message_text(
                "❌ خطا در تایید پرداخت!",
                reply_markup=Keyboards.admin_back_to_payments()
            )
    
    def _get_status_persian(self, status: str) -> str:
        """تبدیل وضعیت به فارسی"""
        status_map = {
            "pending": "در انتظار",
            "success": "موفق",
            "failed": "ناموفق",
            "cancelled": "لغو شده"
        }
        return status_map.get(status, status)
    
    def _get_method_persian(self, method: str) -> str:
        """تبدیل روش پرداخت به فارسی"""
        method_map = {
            "wallet": "کیف پول",
            "online": "درگاه آنلاین",
            "manual": "کارت به کارت"
        }
        return method_map.get(method, method)

# نمونه استفاده
# payment_admin = PaymentAdmin(db_session)
