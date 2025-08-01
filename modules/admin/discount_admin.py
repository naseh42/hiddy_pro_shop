from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.discount_manager import DiscountManager
from utils.helpers import Helpers
from utils.keyboards import Keyboards

class DiscountAdmin:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.discount_manager = DiscountManager(db)
    
    async def show_discounts_list(self, query, page: int = 1):
        """نمایش لیست کدهای تخفیف"""
        per_page = 10
        # در اینجا باید تعداد کل کدها رو محاسبه کنیم
        from models.discount import DiscountCode
        count_result = await self.db.execute(select(func.count(DiscountCode.id)))
        total_discounts = count_result.scalar_one()
        total_pages = (total_discounts + per_page - 1) // per_page
        
        # دریافت کدهای تخفیف
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(DiscountCode)
            .order_by(DiscountCode.created_at.desc())
            .offset(offset).limit(per_page)
        )
        discounts = result.scalars().all()
        
        if not discounts:
            discounts_text = "❌ هیچ کد تخفیفی تعریف نشده است."
        else:
            discounts_text = "🏷️ لیست کدهای تخفیف:\n"
            for i, discount in enumerate(discounts, 1):
                status = "فعال" if discount.is_active else "غیرفعال"
                discount_type = "درصدی" if discount.discount_type == "percentage" else "ثابت"
                
                discounts_text += f"{i}. {discount.code}\n"
                discounts_text += f"   📊 نوع: {discount_type}\n"
                if discount.discount_type == "percentage":
                    discounts_text += f"   💰 مقدار: {discount.discount_value}%\n"
                else:
                    discounts_text += f"   💰 مقدار: {Helpers.format_price(discount.discount_value)}\n"
                discounts_text += f"   📊 وضعیت: {status}\n"
                discounts_text += f"   📊 استفاده: {discount.used_count}/{discount.max_uses if discount.max_uses > 0 else 'نامحدود'}\n"
                discounts_text += f"   🆔 /edit_discount_{discount.id}\n\n"
        
        discounts_info = f"""
🏷️ مدیریت کدهای تخفیف:
صفحه {page} از {total_pages}
تعداد کل کدها: {total_discounts}

{discounts_text}

عملیات موجود:
• ایجاد کد تخفیف جدید: /create_discount
• ویرایش کدهای موجود
• فعال/غیرفعال کردن کدها
• حذف کدها
"""
        
        keyboard = Keyboards.admin_discounts_navigation(page, total_pages)
        await query.edit_message_text(discounts_info, reply_markup=keyboard)
    
    async def show_create_discount_form(self, query):
        """نمایش فرم ایجاد کد تخفیف جدید"""
        form_text = """
➕ ایجاد کد تخفیف جدید:
لطفاً اطلاعات کد تخفیف جدید را به ترتیب زیر وارد کنید:

کد تخفیف:
نوع تخفیف (percentage/fixed):
مقدار تخفیف (درصد یا مبلغ):
توضیحات (اختیاری):
حداکثر استفاده (0 برای نامحدود):
تاریخ شروع (YYYY-MM-DD HH:MM - اختیاری):
تاریخ پایان (YYYY-MM-DD HH:MM - اختیاری):

مثال:
SUMMER20
percentage
20
تخفیف تابستانی
100
2024-07-01 00:00
2024-08-31 23:59
"""
        
        await query.edit_message_text(
            form_text,
            reply_markup=Keyboards.admin_back_to_discounts()
        )
        return "awaiting_discount_data"
    
    async def create_discount_from_data(self, query, discount_data_text):
        """ایجاد کد تخفیف از داده‌های وارد شده"""
        try:
            lines = discount_data_text.strip().split('\n')
            if len(lines) < 3:
                await query.edit_message_text(
                    "❌ اطلاعات ناقص است. لطفاً همه فیلدهای اجباری را وارد کنید.",
                    reply_markup=Keyboards.admin_back_to_discounts()
                )
                return
            
            code = lines[0].strip()
            discount_type = lines[1].strip()
            discount_value = float(lines[2].strip())
            
            description = lines[3].strip() if len(lines) > 3 else None
            max_uses = int(lines[4].strip()) if len(lines) > 4 and lines[4].strip() else 0
            
            # تاریخ‌ها
            from datetime import datetime
            valid_from = None
            valid_until = None
            
            if len(lines) > 5 and lines[5].strip():
                valid_from = datetime.strptime(lines[5].strip(), "%Y-%m-%d %H:%M")
            if len(lines) > 6 and lines[6].strip():
                valid_until = datetime.strptime(lines[6].strip(), "%Y-%m-%d %H:%M")
            
            discount = await self.discount_manager.create_discount_code(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                description=description,
                max_uses=max_uses,
                valid_from=valid_from,
                valid_until=valid_until
            )
            
            if discount:
                await query.edit_message_text(
                    f"✅ کد تخفیف '{discount.code}' با موفقیت ایجاد شد!",
                    reply_markup=Keyboards.admin_back_to_discounts()
                )
            else:
                await query.edit_message_text(
                    "❌ خطا در ایجاد کد تخفیف!",
                    reply_markup=Keyboards.admin_back_to_discounts()
                )
        except Exception as e:
            await query.edit_message_text(
                f"❌ خطا در پردازش اطلاعات: {str(e)}",
                reply_markup=Keyboards.admin_back_to_discounts()
            )
    
    async def show_edit_discount_form(self, query, discount_id):
        """نمایش فرم ویرایش کد تخفیف"""
        from models.discount import DiscountCode
        result = await self.db.execute(
            select(DiscountCode).where(DiscountCode.id == discount_id)
        )
        discount = result.scalar_one_or_none()
        
        if not discount:
            await query.answer("❌ کد تخفیف یافت نشد!")
            return
        
        discount_type = "درصدی" if discount.discount_type == "percentage" else "ثابت"
        status = "فعال" if discount.is_active else "غیرفعال"
        
        form_text = f"""
✏️ ویرایش کد تخفیف: {discount.code}
شناسه کد: {discount.id}

اطلاعات فعلی:
1. کد تخفیف: {discount.code}
2. نوع تخفیف: {discount_type}
3. مقدار تخفیف: {discount.discount_value}
4. توضیحات: {discount.description or 'ندارد'}
5. حداکثر استفاده: {discount.max_uses if discount.max_uses > 0 else 'نامحدود'}
6. استفاده شده: {discount.used_count}
7. تاریخ شروع: {discount.valid_from.strftime('%Y-%m-%d %H:%M') if discount.valid_from else 'ندارد'}
8. تاریخ پایان: {discount.valid_until.strftime('%Y-%m-%d %H:%M') if discount.valid_until else 'ندارد'}
9. وضعیت: {status}

برای ویرایش، شماره فیلد و مقدار جدید را وارد کنید:
مثال: 1. WINTER30

برای حذف کد: /delete_discount_{discount.id}
برای فعال/غیرفعال کردن: /toggle_discount_{discount.id}
"""
        
        await query.edit_message_text(
            form_text,
            reply_markup=Keyboards.admin_back_to_discounts()
        )
        return f"editing_discount_{discount_id}"
    
    async def update_discount_field(self, query, discount_id, field_data):
        """بروزرسانی یک فیلد از کد تخفیف"""
        try:
            from models.discount import DiscountCode
            result = await self.db.execute(
                select(DiscountCode).where(DiscountCode.id == discount_id)
            )
            discount = result.scalar_one_or_none()
            
            if not discount:
                await query.edit_message_text(
                    "❌ کد تخفیف یافت نشد!",
                    reply_markup=Keyboards.admin_back_to_discounts()
                )
                return
            
            # پردازش داده ورودی
            if '. ' in field_data:
                field_num, new_value = field_data.split('. ', 1)
                field_num = int(field_num)
                
                field_mapping = {
                    1: 'code',
                    2: 'discount_type',
                    3: 'discount_value',
                    4: 'description',
                    5: 'max_uses',
                    6: 'used_count',
                    7: 'valid_from',
                    8: 'valid_until',
                    9: 'is_active'
                }
                
                if field_num in field_mapping:
                    field_name = field_mapping[field_num]
                    
                    # تبدیل نوع داده برای فیلدهای خاص
                    if field_name in ['discount_value']:
                        new_value = float(new_value)
                    elif field_name in ['max_uses', 'used_count']:
                        new_value = int(new_value)
                    elif field_name in ['valid_from', 'valid_until']:
                        if new_value.strip():
                            from datetime import datetime
                            new_value = datetime.strptime(new_value.strip(), "%Y-%m-%d %H:%M")
                        else:
                            new_value = None
                    elif field_name in ['is_active']:
                        new_value = new_value.lower() in ['بله', 'yes', 'true', '1', 'فعال']
                    
                    # بروزرسانی فیلد
                    success = await self.discount_manager.update_discount(discount_id, **{field_name: new_value})
                    
                    if success:
                        await query.edit_message_text(
                            f"✅ فیلد {field_name} با موفقیت بروزرسانی شد!",
                            reply_markup=Keyboards.admin_back_to_discounts()
                        )
                    else:
                        await query.edit_message_text(
                            "❌ خطا در بروزرسانی کد تخفیف!",
                            reply_markup=Keyboards.admin_back_to_discounts()
                        )
                else:
                    await query.edit_message_text(
                        "❌ شماره فیلد نامعتبر است!",
                        reply_markup=Keyboards.admin_back_to_discounts()
                    )
            else:
                await query.edit_message_text(
                    "❌ فرمت ورودی نامعتبر است! لطفاً به صورت 'شماره. مقدار جدید' وارد کنید.",
                    reply_markup=Keyboards.admin_back_to_discounts()
                )
        except Exception as e:
            await query.edit_message_text(
                f"❌ خطا در بروزرسانی: {str(e)}",
                reply_markup=Keyboards.admin_back_to_discounts()
            )
    
    async def delete_discount(self, query, discount_id):
        """حذف کد تخفیف"""
        from models.discount import DiscountCode
        result = await self.db.execute(
            select(DiscountCode).where(DiscountCode.id == discount_id)
        )
        discount = result.scalar_one_or_none()
        
        if not discount:
            await query.answer("❌ کد تخفیف یافت نشد!")
            return
        
        success = await self.discount_manager.delete_discount(discount_id)
        if success:
            await query.edit_message_text(
                f"✅ کد تخفیف '{discount.code}' با موفقیت حذف شد!",
                reply_markup=Keyboards.admin_back_to_discounts()
            )
        else:
            await query.edit_message_text(
                "❌ خطا در حذف کد تخفیف!",
                reply_markup=Keyboards.admin_back_to_discounts()
            )
    
    async def toggle_discount_status(self, query, discount_id):
        """فعال/غیرفعال کردن کد تخفیف"""
        from models.discount import DiscountCode
        result = await self.db.execute(
            select(DiscountCode).where(DiscountCode.id == discount_id)
        )
        discount = result.scalar_one_or_none()
        
        if not discount:
            await query.answer("❌ کد تخفیف یافت نشد!")
            return
        
        if discount.is_active:
            success = await self.discount_manager.deactivate_discount(discount_id)
            message = f"✅ کد تخفیف '{discount.code}' غیرفعال شد!"
        else:
            success = await self.discount_manager.activate_discount(discount_id)
            message = f"✅ کد تخفیف '{discount.code}' فعال شد!"
        
        if success:
            await query.edit_message_text(
                message,
                reply_markup=Keyboards.admin_back_to_discounts()
            )
        else:
            await query.edit_message_text(
                "❌ خطا در تغییر وضعیت کد تخفیف!",
                reply_markup=Keyboards.admin_back_to_discounts()
            )
