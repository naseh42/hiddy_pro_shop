from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # اطلاعات پرداخت
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="Toman")
    
    # روش پرداخت
    payment_method = Column(String(50), nullable=False)  # wallet, online, manual
    payment_gateway = Column(String(50), nullable=True)  # نام درگاه (زرین‌پال، نکست‌پی، ...)
    
    # شناسه پرداخت
    transaction_id = Column(String(100), nullable=True)
    authority = Column(String(100), nullable=True)  # برای زرین‌پال
    
    # وضعیت
    status = Column(String(20), default="pending")  # pending, success, failed, cancelled
    
    # توضیحات
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
