from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
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
    product_name = Column(String(100), nullable=True)  # نام محصول در هیدیفای
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # اطلاعات اضافی
    max_ips = Column(Integer, default=1)  # حداکثر IP همزمان
    monthly_package = Column(Boolean, default=False)  # پکیج ماهانه
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
