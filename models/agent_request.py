from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from database import Base

class AgentRequest(Base):
    __tablename__ = "agent_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # اطلاعات درخواست
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)  # تجربه در زمینه مرتبط
    
    # وضعیت
    status = Column(String(20), default="pending")  # pending, approved, rejected
    rejection_reason = Column(Text, nullable=True)  # دلیل رد درخواست
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
