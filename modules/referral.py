from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.referral import Referral
from models.payment import Payment
from datetime import datetime

class ReferralManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_referral(self, referrer_id: int, referred_id: int, 
                            commission_amount: float = 0.0, 
                            order_id: int = None) -> Referral:
        """ایجاد رکورد رفرال جدید"""
        referral = Referral(
            referrer_id=referrer_id,
            referred_id=referred_id,
            commission_amount=commission_amount,
            order_id=order_id
        )
        
        self.db.add(referral)
        await self.db.commit()
        await self.db.refresh(referral)
        return referral
    
    async def get_user_referrals(self, user_id: int, page: int = 1, 
                               per_page: int = 20) -> list:
        """دریافت کاربران معرفی‌شده توسط کاربر"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(User, Referral.created_at)
            .join(Referral, User.id == Referral.referred_id)
            .where(Referral.referrer_id == user_id)
            .order_by(Referral.created_at.desc())
            .offset(offset).limit(per_page)
        )
        return result.all()
    
    async def get_referral_by_users(self, referrer_id: int, referred_id: int) -> Referral:
        """دریافت رکورد رفرال بین دو کاربر"""
        result = await self.db.execute(
            select(Referral).where(
                and_(
                    Referral.referrer_id == referrer_id,
                    Referral.referred_id == referred_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_referral_stats(self, user_id: int) -> dict:
        """دریافت آمار رفرال کاربر"""
        # تعداد کاربران معرفی‌شده
        referred_count_result = await self.db.execute(
            select(func.count(Referral.id)).where(Referral.referrer_id == user_id)
        )
        referred_count = referred_count_result.scalar_one()
        
        # مجموع کمیسیون دریافت‌شده
        commission_result = await self.db.execute(
            select(func.sum(Referral.commission_amount))
            .where(
                and_(
                    Referral.referrer_id == user_id,
                    Referral.commission_status == "paid"
                )
            )
        )
        total_commission = commission_result.scalar_one() or 0.0
        
        # کمیسیون در انتظار پرداخت
        pending_result = await self.db.execute(
            select(func.sum(Referral.commission_amount))
            .where(
                and_(
                    Referral.referrer_id == user_id,
                    Referral.commission_status == "pending"
                )
            )
        )
        pending_commission = pending_result.scalar_one() or 0.0
        
        return {
            "referred_count": referred_count,
            "total_commission": total_commission,
            "pending_commission": pending_commission
        }
    
    async def pay_referral_commission(self, referral_id: int) -> bool:
        """پرداخت کمیسیون رفرال"""
        result = await self.db.execute(
            select(Referral).where(Referral.id == referral_id)
        )
        referral = result.scalar_one_or_none()
        
        if referral and referral.commission_status == "pending":
            referral.commission_status = "paid"
            referral.updated_at = datetime.now()
            
            # افزایش کیف پول کاربر معرف
            from modules.wallet import WalletManager
            wallet_manager = WalletManager(self.db)
            await wallet_manager.add_to_wallet(
                referral.referrer_id,
                referral.commission_amount,
                f"کمیسیون رفرال - کاربر {referral.referred_id}"
            )
            
            await self.db.commit()
            return True
        return False
    
    async def calculate_commission(self, amount: float, commission_rate: float = 10.0) -> float:
        """محاسبه کمیسیون رفرال"""
        return (amount * commission_rate) / 100.0
    
    async def get_pending_commissions(self) -> list:
        """دریافت کمیسیون‌های در انتظار پرداخت"""
        result = await self.db.execute(
            select(Referral).where(Referral.commission_status == "pending")
            .order_by(Referral.created_at)
        )
        return result.scalars().all()
    
    async def get_user_referral_code(self, user_id: int) -> str:
        """دریافت کد رفرال کاربر"""
        result = await self.db.execute(
            select(User.referral_code).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

# نمونه استفاده
# referral_manager = ReferralManager(db_session)
# referral = await referral_manager.create_referral(1, 2, 5000.0)
