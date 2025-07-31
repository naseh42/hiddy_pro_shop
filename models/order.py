from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    
    # اطلاعات سفارش
    plan_name = Column(String(100), nullable=False)
    days = Column(Integer, nullable=False)
    traffic_gb = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # کد تخفیف (در صورت وجود)
    discount_code = Column(String(50), nullable=True)
    discount_amount = Column(Float, default=0.0)
    
    # وضعیت سفارش
    status = Column(String(20), default="pending")  # pending, paid, completed, failed
    
    # اطلاعات هیدیفای
    hiddify_uuid = Column(String(50), nullable=True)
    secret_uuid = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
