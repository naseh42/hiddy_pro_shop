from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.plan_manager import PlanManager
from utils.helpers import Helpers
from utils.keyboards import Keyboards

class PlanAdmin:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.plan_manager = PlanManager(db)
    
    async def show_plans_list(self, query, page: int = 1):
        """نمایش لیست پلن‌ها برای ادمین"""
        per_page = 10
        plans = await self.plan_manager.get_all_plans(page=page, per_page=per_page)
        total_plans = await self.plan_manager.get_plans_count()
        total_pages = (total_plans + per_page - 1) // per_page
        
        if not plans:
            plans_text = "❌ هیچ پلنی تعریف نشده است."
        else:
            plans_text = "📋 لیست پلن‌های تعریف‌شده:\n"
            for i, plan in enumerate(plans, 1):
                status = "فعال" if plan.is_active else "غیرفعال"
                plans_text += f"{i}. {plan.name}\n"
                plans_text += f"   ⏱️ {Helpers.format_days(plan.days)}\n"
                plans_text += f"   📊 {Helpers.format_traffic(plan.traffic_gb)}\n"
                plans_text += f"   💰 {Helpers.format_price(plan.price)}\n"
                plans_text += f"   📊 وضعیت: {status}\n"
                plans_text += f"   🆔 /edit_plan_{plan.id}\n\n"
        
        plans_info = f"""
📋 مدیریت پلن‌ها:
صفحه {page} از {total_pages}
تعداد کل پلن‌ها: {total_plans}

{plans_text}

عملیات موجود:
• ایجاد پلن جدید: /create_plan
• ویرایش پلن: روی ID کلیک کنید
• فعال/غیرفعال کردن پلن‌ها
• حذف پلن‌ها
"""
        
        keyboard = Keyboards.admin_plans_navigation(page, total_pages)
        await query.edit_message_text(plans_info, reply_markup=keyboard)
    
    async def show_create_plan_form(self, query):
        """نمایش فرم ایجاد پلن جدید"""
        form_text = """
➕ ایجاد پلن جدید:
لطفاً اطلاعات پلن جدید را به ترتیب زیر وارد کنید:

نام پلن:
تعداد روزها:
 trafic به GB:
قیمت به تومان:
توضیحات (اختیاری):
حالت هیدیفای (no_reset/reset):
نام محصول در هیدیفای (اختیاری):
حداکثر IP همزمان:
پکیج ماهانه (بله/خیر):

مثال:
ماهیانه Vip
30
100
150000
پلن ویژه با ترافیک بالا
no_reset
Vip Monthly
5
بله
"""
        
        await query.edit_message_text(
            form_text,
            reply_markup=Keyboards.admin_back_to_plans()
        )
        return "awaiting_plan_data"
    
    async def create_plan_from_data(self, query, plan_data_text):
        """ایجاد پلن از داده‌های وارد شده"""
        try:
            lines = plan_data_text.strip().split('\n')
            if len(lines) < 4:
                await query.edit_message_text(
                    "❌ اطلاعات ناقص است. لطفاً همه فیلدهای اجباری را وارد کنید.",
                    reply_markup=Keyboards.admin_back_to_plans()
                )
                return
            
            name = lines[0].strip()
            days = int(lines[1].strip())
            traffic_gb = float(lines[2].strip())
            price = float(lines[3].strip())
            
            description = lines[4].strip() if len(lines) > 4 else None
            hiddify_mode = lines[5].strip() if len(lines) > 5 else "no_reset"
            product_name = lines[6].strip() if len(lines) > 6 else None
            max_ips = int(lines[7].strip()) if len(lines) > 7 else 1
            monthly_package = lines[8].strip().lower() in ['بله', 'yes', 'true', '1'] if len(lines) > 8 else False
            
            plan = await self.plan_manager.create_plan(
                name=name,
                days=days,
                traffic_gb=traffic_gb,
                price=price,
                description=description,
                hiddify_mode=hiddify_mode,
                product_name=product_name,
                max_ips=max_ips,
                monthly_package=monthly_package
            )
            
            if plan:
                await query.edit_message_text(
                    f"✅ پلن '{plan.name}' با موفقیت ایجاد شد!",
                    reply_markup=Keyboards.admin_back_to_plans()
                )
            else:
                await query.edit_message_text(
                    "❌ خطا در ایجاد پلن!",
                    reply_markup=Keyboards.admin_back_to_plans()
                )
        except Exception as e:
            await query.edit_message_text(
                f"❌ خطا در پردازش اطلاعات: {str(e)}",
                reply_markup=Keyboards.admin_back_to_plans()
            )
    
    async def show_edit_plan_form(self, query, plan_id):
        """نمایش فرم ویرایش پلن"""
        plan = await self.plan_manager.get_plan_by_id(plan_id)
        if not plan:
            await query.answer("❌ پلن یافت نشد!")
            return
        
        form_text = f"""
✏️ ویرایش پلن: {plan.name}
شناسه پلن: {plan.id}

اطلاعات فعلی:
1. نام پلن: {plan.name}
2. تعداد روزها: {plan.days}
3. trafic به GB: {plan.traffic_gb}
4. قیمت به تومان: {plan.price}
5. توضیحات: {plan.description or 'ندارد'}
6. حالت هیدیفای: {plan.hiddify_mode}
7. نام محصول در هیدیفای: {plan.product_name or 'ندارد'}
8. حداکثر IP همزمان: {plan.max_ips}
9. پکیج ماهانه: {'بله' if plan.monthly_package else 'خیر'}
10. وضعیت: {'فعال' if plan.is_active else 'غیرفعال'}

برای ویرایش، شماره فیلد و مقدار جدید را وارد کنید:
مثال: 1. پلن طلایی Vip

برای حذف پلن: /delete_plan_{plan.id}
برای فعال/غیرفعال کردن: /toggle_plan_{plan.id}
"""
        
        await query.edit_message_text(
            form_text,
            reply_markup=Keyboards.admin_back_to_plans()
        )
        return f"editing_plan_{plan_id}"
    
    async def update_plan_field(self, query, plan_id, field_data):
        """بروزرسانی یک فیلد از پلن"""
        try:
            plan = await self.plan_manager.get_plan_by_id(plan_id)
            if not plan:
                await query.edit_message_text(
                    "❌ پلن یافت نشد!",
                    reply_markup=Keyboards.admin_back_to_plans()
                )
                return
            
            # پردازش داده ورودی
            if '. ' in field_data:
                field_num, new_value = field_data.split('. ', 1)
                field_num = int(field_num)
                
                field_mapping = {
                    1: 'name',
                    2: 'days',
                    3: 'traffic_gb',
                    4: 'price',
                    5: 'description',
                    6: 'hiddify_mode',
                    7: 'product_name',
                    8: 'max_ips',
                    9: 'monthly_package',
                    10: 'is_active'
                }
                
                if field_num in field_mapping:
                    field_name = field_mapping[field_num]
                    
                    # تبدیل نوع داده برای فیلدهای عددی
                    if field_name in ['days', 'max_ips']:
                        new_value = int(new_value)
                    elif field_name in ['traffic_gb', 'price']:
                        new_value = float(new_value)
                    elif field_name in ['monthly_package', 'is_active']:
                        new_value = new_value.lower() in ['بله', 'yes', 'true', '1', 'فعال']
                    
                    # بروزرسانی فیلد
                    success = await self.plan_manager.update_plan(plan_id, **{field_name: new_value})
                    
                    if success:
                        await query.edit_message_text(
                            f"✅ فیلد {field_name} با موفقیت بروزرسانی شد!",
                            reply_markup=Keyboards.admin_back_to_plans()
                        )
                    else:
                        await query.edit_message_text(
                            "❌ خطا در بروزرسانی پلن!",
                            reply_markup=Keyboards.admin_back_to_plans()
                        )
                else:
                    await query.edit_message_text(
                        "❌ شماره فیلد نامعتبر است!",
                        reply_markup=Keyboards.admin_back_to_plans()
                    )
            else:
                await query.edit_message_text(
                    "❌ فرمت ورودی نامعتبر است! لطفاً به صورت 'شماره. مقدار جدید' وارد کنید.",
                    reply_markup=Keyboards.admin_back_to_plans()
                )
        except Exception as e:
            await query.edit_message_text(
                f"❌ خطا در بروزرسانی: {str(e)}",
                reply_markup=Keyboards.admin_back_to_plans()
            )
    
    async def delete_plan(self, query, plan_id):
        """حذف پلن"""
        plan = await self.plan_manager.get_plan_by_id(plan_id)
        if not plan:
            await query.answer("❌ پلن یافت نشد!")
            return
        
        success = await self.plan_manager.delete_plan(plan_id)
        if success:
            await query.edit_message_text(
                f"✅ پلن '{plan.name}' با موفقیت حذف شد!",
                reply_markup=Keyboards.admin_back_to_plans()
            )
        else:
            await query.edit_message_text(
                "❌ خطا در حذف پلن!",
                reply_markup=Keyboards.admin_back_to_plans()
            )
    
    async def toggle_plan_status(self, query, plan_id):
        """فعال/غیرفعال کردن پلن"""
        plan = await self.plan_manager.get_plan_by_id(plan_id)
        if not plan:
            await query.answer("❌ پلن یافت نشد!")
            return
        
        if plan.is_active:
            success = await self.plan_manager.deactivate_plan(plan_id)
            message = f"✅ پلن '{plan.name}' غیرفعال شد!"
        else:
            success = await self.plan_manager.activate_plan(plan_id)
            message = f"✅ پلن '{plan.name}' فعال شد!"
        
        if success:
            await query.edit_message_text(
                message,
                reply_markup=Keyboards.admin_back_to_plans()
            )
        else:
            await query.edit_message_text(
                "❌ خطا در تغییر وضعیت پلن!",
                reply_markup=Keyboards.admin_back_to_plans()
            )
