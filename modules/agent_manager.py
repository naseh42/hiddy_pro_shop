from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.agent_request import AgentRequest
from datetime import datetime

class AgentManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_agent_request(self, user_id: int, full_name: str, phone: str,
                                 email: str = None, address: str = None, 
                                 experience: str = None) -> AgentRequest:
        """ایجاد درخواست نمایندگی جدید"""
        agent_request = AgentRequest(
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            experience=experience
        )
        
        self.db.add(agent_request)
        await self.db.commit()
        await self.db.refresh(agent_request)
        return agent_request
    
    async def get_agent_request_by_id(self, request_id: int) -> AgentRequest:
        """دریافت درخواست نمایندگی بر اساس آیدی"""
        result = await self.db.execute(
            select(AgentRequest).where(AgentRequest.id == request_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_agent_request(self, user_id: int) -> AgentRequest:
        """دریافت درخواست نمایندگی کاربر"""
        result = await self.db.execute(
            select(AgentRequest).where(AgentRequest.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_requests(self, page: int = 1, per_page: int = 20) -> list:
        """دریافت درخواست‌های در انتظار تایید"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(AgentRequest)
            .where(AgentRequest.status == "pending")
            .order_by(AgentRequest.created_at.desc())
            .offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def approve_agent_request(self, request_id: int) -> bool:
        """تایید درخواست نمایندگی"""
        result = await self.db.execute(
            select(AgentRequest).where(AgentRequest.id == request_id)
        )
        request = result.scalar_one_or_none()
        
        if request and request.status == "pending":
            request.status = "approved"
            request.updated_at = datetime.now()
            
            # تغییر سطح دسترسی کاربر به نماینده
            from modules.user_manager import UserManager
            user_manager = UserManager(self.db)
            await user_manager.set_user_agent(request.user_id, True)
            
            await self.db.commit()
            return True
        return False
    
    async def reject_agent_request(self, request_id: int, reason: str = None) -> bool:
        """رد درخواست نمایندگی"""
        result = await self.db.execute(
            select(AgentRequest).where(AgentRequest.id == request_id)
        )
        request = result.scalar_one_or_none()
        
        if request and request.status == "pending":
            request.status = "rejected"
            request.rejection_reason = reason
            request.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def get_requests_count(self, status: str = None) -> int:
        """دریافت تعداد درخواست‌ها"""
        query = select(func.count(AgentRequest.id))
        if status:
            query = query.where(AgentRequest.status == status)
        
        result = await self.db.execute(query)
        return result.scalar_one()

# نمونه استفاده
# agent_manager = AgentManager(db_session)
# request = await agent_manager.create_agent_request(1, "نام کامل", "09123456789")
