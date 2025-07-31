from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # کاربر معرف
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False)   # کاربر معرفی‌شده
    
    # پورسانت
    commission_amount = Column(Float, default=0.0)
    commission_status = Column(String(20), default="pending")  # pending, paid
    
    # سفارش مربوطه (در صورت وجود)
    order_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
