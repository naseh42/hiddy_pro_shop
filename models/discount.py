from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from database import Base

class DiscountCode(Base):
    __tablename__ = "discount_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200), nullable=True)
    
    # نوع تخفیف
    discount_type = Column(String(20), default="percentage")  # percentage, fixed
    discount_value = Column(Float, nullable=False)  # درصد یا مبلغ ثابت
    
    # محدودیت‌ها
    max_uses = Column(Integer, default=0)  # 0 = نامحدود
    used_count = Column(Integer, default=0)
    
    # زمان محدودیت
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
