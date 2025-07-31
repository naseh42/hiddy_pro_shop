from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # مشخصات پلن
    days = Column(Integer, nullable=False)  # تعداد روزها
    traffic_gb = Column(Float, nullable=False)  # ترافیک به گیگابایت
    
    # قیمت
    price = Column(Float, nullable=False)  # به تومان
    
    # تنظیمات هیدیفای
    hiddify_mode = Column(String(50), default="no_reset")  # no_reset, reset
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
