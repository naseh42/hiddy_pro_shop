from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.plan import Plan
from models.payment import Payment
from models.order import Order
from models.referral import Referral
from datetime import datetime, timedelta

class AdminPanel:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_system_stats(self) -> dict:
        """دریافت آمار کلی سیستم"""
        # تعداد کاربران
        users_count = await self.db.execute(select(func.count(User.id)))
        total_users = users_count.scalar_one()
        
        # تعداد پلن‌ها
        plans_count = await self.db.execute(select(func.count(Plan.id)))
        total_plans = plans_count.scalar_one()
        
        # تعداد سفارشات
        orders_count = await self.db.execute(select(func.count(Order.id)))
        total_orders = orders_count.scalar_one()
        
        # درآمد کل (پرداخت‌های موفق)
        revenue_result = await self.db.execute(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
        )
        total_revenue = revenue_result.scalar_one() or 0.0
        
        # کاربران امروز
        today = datetime.now().date()
        today_users_result = await self.db.execute(
            select(func.count(User.id))
            .where(func.date(User.created_at) == today)
        )
        today_users = today_users_result.scalar_one()
        
        return {
            "total_users": total_users,
            "total_plans": total_plans,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "today_users": today_users
        }
    
    async def get_recent_users(self, limit: int = 10) -> list:
        """دریافت جدیدترین کاربران"""
        result = await self.db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_payments(self, limit: int = 10) -> list:
        """دریافت جدیدترین پرداخت‌ها"""
        result = await self.db.execute(
            select(Payment)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_by_id(self, user_id: int) -> User:
        """دریافت اطلاعات کاربر بر اساس آیدی"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def ban_user(self, user_id: int) -> bool:
        """مسدود کردن کاربر"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_active = False
            user.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def unban_user(self, user_id: int) -> bool:
        """رفع مسدودی کاربر"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_active = True
            user.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def set_user_admin(self, user_id: int, is_admin: bool) -> bool:
        """تعیین کاربر به عنوان ادمین"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_admin = is_admin
            user.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def get_payment_statistics(self, days: int = 30) -> dict:
        """دریافت آمار پرداخت‌ها در بازه زمانی"""
        start_date = datetime.now() - timedelta(days=days)
        
        # پرداخت‌های موفق
        success_result = await self.db.execute(
            select(func.count(Payment.id), func.sum(Payment.amount))
            .where(
                and_(
                    Payment.status == "success",
                    Payment.created_at >= start_date
                )
            )
        )
        success_count, success_amount = success_result.fetchone() or (0, 0)
        
        # پرداخت‌های ناموفق
        failed_result = await self.db.execute(
            select(func.count(Payment.id))
            .where(
                and_(
                    Payment.status == "failed",
                    Payment.created_at >= start_date
                )
            )
        )
        failed_count = failed_result.scalar_one()
        
        return {
            "success_count": success_count or 0,
            "success_amount": success_amount or 0.0,
            "failed_count": failed_count or 0,
            "conversion_rate": (success_count / (success_count + failed_count) * 100) if (success_count + failed_count) > 0 else 0
        }
    
    async def get_top_referrers(self, limit: int = 10) -> list:
        """دریافت بهترین کاربران رفرال‌دهنده"""
        result = await self.db.execute(
            select(User, func.count(Referral.id).label('referral_count'))
            .join(Referral, User.id == Referral.referrer_id)
            .where(Referral.commission_status == "paid")
            .group_by(User.id)
            .order_by(func.count(Referral.id).desc())
            .limit(limit)
        )
        return result.all()
    
    async def get_system_logs(self, limit: int = 50) -> list:
        """دریافت لاگ‌های سیستم (برای نسخه‌های بعدی)"""
        # این بخش بعداً پیاده‌سازی می‌شه
        return []

# نمونه استفاده
# admin_panel = AdminPanel(db_session)
# stats = await admin_panel.get_system_stats()
