from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.payment import Payment
from datetime import datetime

class WalletManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_wallet_balance(self, user_id: int) -> float:
        """دریافت موجودی کیف پول کاربر"""
        result = await self.db.execute(
            select(User.wallet_balance).where(User.id == user_id)
        )
        balance = result.scalar_one_or_none()
        return balance if balance is not None else 0.0
    
    async def add_to_wallet(self, user_id: int, amount: float, 
                           description: str = None, payment_id: int = None) -> bool:
        """افزایش موجودی کیف پول"""
        if amount <= 0:
            return False
        
        # بروزرسانی موجودی
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.wallet_balance += amount
            user.updated_at = datetime.now()
            
            # ثبت تراکنش
            transaction = Payment(
                user_id=user_id,
                amount=amount,
                payment_method="wallet",
                description=description or "افزایش موجودی کیف پول",
                status="success"
            )
            self.db.add(transaction)
            
            await self.db.commit()
            return True
        return False
    
    async def deduct_from_wallet(self, user_id: int, amount: float, 
                               description: str = None) -> bool:
        """کسر از کیف پول"""
        if amount <= 0:
            return False
        
        # بررسی موجودی
        balance = await self.get_user_wallet_balance(user_id)
        if balance < amount:
            return False
        
        # بروزرسانی موجودی
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.wallet_balance -= amount
            user.updated_at = datetime.now()
            
            # ثبت تراکنش
            transaction = Payment(
                user_id=user_id,
                amount=-amount,  # منفی برای کسر
                payment_method="wallet",
                description=description or "کسر از کیف پول",
                status="success"
            )
            self.db.add(transaction)
            
            await self.db.commit()
            return True
        return False
    
    async def transfer_to_wallet(self, from_user_id: int, to_user_id: int, 
                               amount: float, description: str = None) -> bool:
        """انتقال بین کیف پول‌ها"""
        if amount <= 0:
            return False
        
        # بررسی موجودی فرستنده
        from_balance = await self.get_user_wallet_balance(from_user_id)
        if from_balance < amount:
            return False
        
        # کسر از فرستنده
        if not await self.deduct_from_wallet(
            from_user_id, amount, 
            f"انتقال به کاربر {to_user_id} - {description or ''}"
        ):
            return False
        
        # افزایش به گیرنده
        if not await self.add_to_wallet(
            to_user_id, amount,
            f"دریافت از کاربر {from_user_id} - {description or ''}"
        ):
            # برگشت مبلغ به فرستنده در صورت خطا
            await self.add_to_wallet(
                from_user_id, amount,
                "برگشت مبلغ به دلیل خطا در انتقال"
            )
            return False
        
        return True
    
    async def get_wallet_transactions(self, user_id: int, page: int = 1, 
                                    per_page: int = 20) -> list:
        """دریافت تراکنش‌های کیف پول"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Payment)
            .where(
                and_(
                    Payment.user_id == user_id,
                    Payment.payment_method == "wallet"
                )
            )
            .order_by(Payment.created_at.desc())
            .offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def set_wallet_balance(self, user_id: int, balance: float) -> bool:
        """تنظیم موجودی کیف پول (برای ادمین)"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.wallet_balance = max(0, balance)  # جلوگیری از منفی
            user.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False

# نمونه استفاده
# wallet_manager = WalletManager(db_session)
# await wallet_manager.add_to_wallet(1, 50000.0, "شارژ کیف پول")
