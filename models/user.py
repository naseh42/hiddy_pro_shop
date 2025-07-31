from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # سطح دسترسی
    is_admin = Column(Boolean, default=False)
    is_agent = Column(Boolean, default=False)
    
    # کیف پول
    wallet_balance = Column(Float, default=0.0)
    
    # رفرال
    referral_code = Column(String(50), unique=True, index=True)
    referred_by = Column(Integer, nullable=True)  # آیدی کاربر معرف
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UserHiddify(Base):
    """ارتباط کاربران ربات با کاربران هیدیفای"""
    __tablename__ = "user_hiddify"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # آیدی کاربر ربات
    hiddify_uuid = Column(String(50), unique=True, index=True, nullable=False)
    secret_uuid = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
