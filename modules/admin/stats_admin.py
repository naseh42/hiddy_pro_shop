from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.plan import Plan
from models.payment import Payment
from models.order import Order
from models.referral import Referral
from datetime import datetime, timedelta

class StatsAdmin:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_system_stats(self) -> dict:
        """دریافت آمار کلی سیستم"""
        # تعداد کاربران
        users_count = await self.db.execute(select(func.count(User.id)))
        total_users = users_count.scalar_one()
        
        # تعداد کاربران فعال
        active_users_count = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_count.scalar_one()
        
        # تعداد کاربران ادمین
        admin_users_count = await self.db.execute(
            select(func.count(User.id)).where(User.is_admin == True)
        )
        admin_users = admin_users_count.scalar_one()
        
        # تعداد پلن‌ها
        plans_count = await self.db.execute(select(func.count(Plan.id)))
        total_plans = plans_count.scalar_one()
        
        # تعداد پلن‌های فعال
        active_plans_count = await self.db.execute(
            select(func.count(Plan.id)).where(Plan.is_active == True)
        )
        active_plans = active_plans_count.scalar_one()
        
        # تعداد سفارشات
        orders_count = await self.db.execute(select(func.count(Order.id)))
        total_orders = orders_count.scalar_one()
        
        # تعداد سفارشات امروز
        today = datetime.now().date()
        today_orders_count = await self.db.execute(
            select(func.count(Order.id))
            .where(func.date(Order.created_at) == today)
        )
        today_orders = today_orders_count.scalar_one()
        
        # درآمد کل (پرداخت‌های موفق)
        revenue_result = await self.db.execute(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
        )
        total_revenue = revenue_result.scalar_one() or 0.0
        
        # درآمد امروز
        today_revenue_result = await self.db.execute(
            select(func.sum(Payment.amount))
            .where(
                and_(
                    Payment.status == "success",
                    func.date(Payment.created_at) == today
                )
            )
        )
        today_revenue = today_revenue_result.scalar_one() or 0.0
        
        # کاربران امروز
        today_users_result = await self.db.execute(
            select(func.count(User.id))
            .where(func.date(User.created_at) == today)
        )
        today_users = today_users_result.scalar_one()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "total_plans": total_plans,
            "active_plans": active_plans,
            "total_orders": total_orders,
            "today_orders": today_orders,
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
            "today_users": today_users
        }
    
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
        success_data = success_result.fetchone()
        success_count = success_data[0] if success_data else 0
        success_amount = success_data[1] if success_data else 0.0
        
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
        failed_count = failed_result.scalar_one() or 0
        
        # پرداخت‌های در انتظار
        pending_result = await self.db.execute(
            select(func.count(Payment.id))
            .where(
                and_(
                    Payment.status == "pending",
                    Payment.created_at >= start_date
                )
            )
        )
        pending_count = pending_result.scalar_one() or 0
        
        total_count = (success_count or 0) + (failed_count or 0) + (pending_count or 0)
        conversion_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "success_count": success_count or 0,
            "success_amount": success_amount or 0.0,
            "failed_count": failed_count or 0,
            "pending_count": pending_count or 0,
            "conversion_rate": conversion_rate
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

# نمونه استفاده
# stats_admin = StatsAdmin(db_session)
# stats = await stats_admin.get_system_stats()
