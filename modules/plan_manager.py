from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.plan import Plan
from datetime import datetime

class PlanManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_plan(self, name: str, days: int, traffic_gb: float, 
                         price: float, description: str = None, 
                         hiddify_mode: str = "no_reset", product_name: str = None,
                         max_ips: int = 1, monthly_package: bool = False) -> Plan:
        """ایجاد پلن جدید"""
        # محاسبه sort_order برای آخرین موقعیت
        result = await self.db.execute(select(func.max(Plan.sort_order)))
        max_order = result.scalar_one() or 0
        
        plan = Plan(
            name=name,
            days=days,
            traffic_gb=traffic_gb,
            price=price,
            description=description,
            hiddify_mode=hiddify_mode,
            product_name=product_name,
            max_ips=max_ips,
            monthly_package=monthly_package,
            sort_order=max_order + 1
        )
        
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan
    
    async def get_plan_by_id(self, plan_id: int) -> Plan:
        """دریافت پلن بر اساس آیدی"""
        result = await self.db.execute(
            select(Plan).where(Plan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_plans(self) -> list:
        """دریافت پلن‌های فعال"""
        result = await self.db.execute(
            select(Plan).where(Plan.is_active == True).order_by(Plan.sort_order)
        )
        return result.scalars().all()
    
    async def get_all_plans(self, page: int = 1, per_page: int = 50) -> list:
        """دریافت همه پلن‌ها با صفحه‌بندی"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Plan).order_by(Plan.sort_order).offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def update_plan(self, plan_id: int, **kwargs) -> bool:
        """بروزرسانی پلن"""
        plan = await self.get_plan_by_id(plan_id)
        if plan:
            for key, value in kwargs.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            plan.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def delete_plan(self, plan_id: int) -> bool:
        """حذف پلن"""
        plan = await self.get_plan_by_id(plan_id)
        if plan:
            await self.db.delete(plan)
            await self.db.commit()
            return True
        return False
    
    async def activate_plan(self, plan_id: int) -> bool:
        """فعال کردن پلن"""
        return await self.update_plan(plan_id, is_active=True)
    
    async def deactivate_plan(self, plan_id: int) -> bool:
        """غیرفعال کردن پلن"""
        return await self.update_plan(plan_id, is_active=False)
    
    async def search_plans(self, query: str) -> list:
        """جستجو در پلن‌ها"""
        result = await self.db.execute(
            select(Plan).where(
                and_(
                    Plan.is_active == True,
                    Plan.name.contains(query)
                )
            ).order_by(Plan.sort_order)
        )
        return result.scalars().all()
    
    async def reorder_plans(self, plan_ids: list) -> bool:
        """تغییر ترتیب پلن‌ها"""
        try:
            for index, plan_id in enumerate(plan_ids):
                await self.update_plan(plan_id, sort_order=index + 1)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            return False
    
    async def get_plans_count(self) -> int:
        """دریافت تعداد کل پلن‌ها"""
        result = await self.db.execute(select(func.count(Plan.id)))
        return result.scalar_one()

# نمونه استفاده
# plan_manager = PlanManager(db_session)
# plan = await plan_manager.create_plan("ماهیانه", 30, 50.0, 50000.0)
