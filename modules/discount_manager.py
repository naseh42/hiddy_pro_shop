from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.discount import DiscountCode
from datetime import datetime

class DiscountManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_discount_code(self, code: str, discount_type: str, 
                                 discount_value: float, description: str = None,
                                 max_uses: int = 0, valid_from: datetime = None,
                                 valid_until: datetime = None) -> DiscountCode:
        """ایجاد کد تخفیف جدید"""
        discount = DiscountCode(
            code=code,
            description=description,
            discount_type=discount_type,
            discount_value=discount_value,
            max_uses=max_uses,
            valid_from=valid_from,
            valid_until=valid_until
        )
        
        self.db.add(discount)
        await self.db.commit()
        await self.db.refresh(discount)
        return discount
    
    async def get_discount_by_code(self, code: str) -> DiscountCode:
        """دریافت کد تخفیف بر اساس کد"""
        result = await self.db.execute(
            select(DiscountCode).where(DiscountCode.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_active_discounts(self, page: int = 1, per_page: int = 20) -> list:
        """دریافت کدهای تخفیف فعال"""
        offset = (page - 1) * per_page
        now = datetime.now()
        
        result = await self.db.execute(
            select(DiscountCode)
            .where(
                and_(
                    DiscountCode.is_active == True,
                    (DiscountCode.valid_from.is_(None) | (DiscountCode.valid_from <= now)),
                    (DiscountCode.valid_until.is_(None) | (DiscountCode.valid_until >= now)),
                    (DiscountCode.max_uses == 0) | (DiscountCode.used_count < DiscountCode.max_uses)
                )
            )
            .order_by(DiscountCode.created_at.desc())
            .offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def update_discount(self, discount_id: int, **kwargs) -> bool:
        """بروزرسانی کد تخفیف"""
        result = await self.db.execute(
            select(DiscountCode).where(DiscountCode.id == discount_id)
        )
        discount = result.scalar_one_or_none()
        
        if discount:
            for key, value in kwargs.items():
                if hasattr(discount, key):
                    setattr(discount, key, value)
            discount.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def delete_discount(self, discount_id: int) -> bool:
        """حذف کد تخفیف"""
        result = await self.db.execute(
            select(DiscountCode).where(DiscountCode.id == discount_id)
        )
        discount = result.scalar_one_or_none()
        
        if discount:
            await self.db.delete(discount)
            await self.db.commit()
            return True
        return False
    
    async def activate_discount(self, discount_id: int) -> bool:
        """فعال کردن کد تخفیف"""
        return await self.update_discount(discount_id, is_active=True)
    
    async def deactivate_discount(self, discount_id: int) -> bool:
        """غیرفعال کردن کد تخفیف"""
        return await self.update_discount(discount_id, is_active=False)
    
    async def use_discount_code(self, discount_id: int) -> bool:
        """استفاده از کد تخفیف"""
        result = await self.db.execute(
            select(DiscountCode).where(DiscountCode.id == discount_id)
        )
        discount = result.scalar_one_or_none()
        
        if discount and self._is_discount_valid(discount):
            discount.used_count += 1
            discount.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    def _is_discount_valid(self, discount: DiscountCode) -> bool:
        """بررسی اعتبار کد تخفیف"""
        now = datetime.now()
        
        # بررسی فعال بودن
        if not discount.is_active:
            return False
        
        # بررسی تاریخ شروع
        if discount.valid_from and discount.valid_from > now:
            return False
        
        # بررسی تاریخ پایان
        if discount.valid_until and discount.valid_until < now:
            return False
        
        # بررسی تعداد استفاده
        if discount.max_uses > 0 and discount.used_count >= discount.max_uses:
            return False
        
        return True
    
    async def calculate_discount_amount(self, discount: DiscountCode, original_amount: float) -> float:
        """محاسبه مبلغ تخفیف"""
        if discount.discount_type == "percentage":
            return (original_amount * discount.discount_value) / 100
        elif discount.discount_type == "fixed":
            return min(discount.discount_value, original_amount)
        return 0.0

# نمونه استفاده
# discount_manager = DiscountManager(db_session)
# discount = await discount_manager.create_discount_code("SUMMER20", "percentage", 20.0)
