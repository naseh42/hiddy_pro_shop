from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.payment import Payment
from models.user import User
from datetime import datetime, timedelta

class PaymentManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_payment(self, user_id: int, amount: float, 
                           payment_method: str, order_id: int = None,
                           description: str = None, 
                           payment_gateway: str = None) -> Payment:
        """ایجاد پرداخت جدید"""
        payment = Payment(
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            order_id=order_id,
            description=description,
            payment_gateway=payment_gateway,
            transaction_id=self._generate_transaction_id()
        )
        
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    def _generate_transaction_id(self) -> str:
        """تولید شناسه تراکنش منحصر به فرد"""
        import uuid
        return str(uuid.uuid4()).replace('-', '')[:16]
    
    async def get_payment_by_id(self, payment_id: int) -> Payment:
        """دریافت پرداخت بر اساس آیدی"""
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_payment_by_transaction_id(self, transaction_id: str) -> Payment:
        """دریافت پرداخت بر اساس شناسه تراکنش"""
        result = await self.db.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def update_payment_status(self, payment_id: int, status: str, 
                                  transaction_id: str = None, 
                                  authority: str = None) -> bool:
        """بروزرسانی وضعیت پرداخت"""
        payment = await self.get_payment_by_id(payment_id)
        if payment:
            payment.status = status
            if transaction_id:
                payment.transaction_id = transaction_id
            if authority:
                payment.authority = authority
            payment.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def get_user_payments(self, user_id: int, page: int = 1, 
                               per_page: int = 20) -> list:
        """دریافت پرداخت‌های کاربر"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def get_pending_payments(self, page: int = 1, per_page: int = 20) -> list:
        """دریافت پرداخت‌های در انتظار تایید"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Payment)
            .where(Payment.status == "pending")
            .order_by(Payment.created_at.desc())
            .offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def verify_payment(self, payment_id: int, is_verified: bool, 
                           transaction_id: str = None) -> bool:
        """تایید یا رد پرداخت"""
        status = "success" if is_verified else "failed"
        return await self.update_payment_status(
            payment_id, status, transaction_id
        )
    
    async def get_payment_statistics(self, days: int = 30) -> dict:
        """دریافت آمار پرداخت‌ها"""
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
    
    async def get_payments_count(self) -> int:
        """دریافت تعداد کل پرداخت‌ها"""
        result = await self.db.execute(select(func.count(Payment.id)))
        return result.scalar_one()
    
    async def get_success_payments_count(self) -> int:
        """دریافت تعداد پرداخت‌های موفق"""
        result = await self.db.execute(
            select(func.count(Payment.id)).where(Payment.status == "success")
        )
        return result.scalar_one()
    
    async def get_failed_payments_count(self) -> int:
        """دریافت تعداد پرداخت‌های ناموفق"""
        result = await self.db.execute(
            select(func.count(Payment.id)).where(Payment.status == "failed")
        )
        return result.scalar_one()
    
    async def get_pending_payments_count(self) -> int:
        """دریافت تعداد پرداخت‌های در انتظار"""
        result = await self.db.execute(
            select(func.count(Payment.id)).where(Payment.status == "pending")
        )
        return result.scalar_one()

# نمونه استفاده
# payment_manager = PaymentManager(db_session)
# payment = await payment_manager.create_payment(1, 50000.0, "online")
