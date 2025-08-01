from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User, UserHiddify
from utils.helpers import Helpers
from datetime import datetime

class UserManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, telegram_id: int, first_name: str = None, 
                         last_name: str = None, username: str = None, 
                         phone: str = None) -> User:
        """ایجاد کاربر جدید"""
        # بررسی وجود کاربر
        existing_user = await self.get_user_by_telegram_id(telegram_id)
        if existing_user:
            return existing_user
        
        # ایجاد کاربر جدید
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone=phone,
            referral_code=Helpers.generate_referral_code()
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """دریافت کاربر بر اساس آیدی تلگرام"""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> User:
        """دریافت کاربر بر اساس آیدی"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_referral_code(self, referral_code: str) -> User:
        """دریافت کاربر بر اساس کد رفرال"""
        result = await self.db.execute(
            select(User).where(User.referral_code == referral_code)
        )
        return result.scalar_one_or_none()
    
    async def update_user_wallet(self, user_id: int, amount: float) -> bool:
        """بروزرسانی کیف پول کاربر"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.wallet_balance += amount
            user.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def link_hiddify_user(self, user_id: int, hiddify_uuid: str, secret_uuid: str) -> bool:
        """اتصال کاربر ربات به کاربر هیدیفای"""
        link = UserHiddify(
            user_id=user_id,
            hiddify_uuid=hiddify_uuid,
            secret_uuid=secret_uuid
        )
        self.db.add(link)
        await self.db.commit()
        return True
    
    async def get_hiddify_user_link(self, user_id: int) -> UserHiddify:
        """دریافت ارتباط کاربر با هیدیفای"""
        result = await self.db.execute(
            select(UserHiddify).where(UserHiddify.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_users(self, page: int = 1, per_page: int = 50) -> list:
        """دریافت همه کاربران با صفحه‌بندی"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def search_users(self, query: str, page: int = 1, per_page: int = 50) -> list:
        """جستجو در کاربران"""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(User)
            .where(
                User.first_name.contains(query) | 
                User.last_name.contains(query) | 
                User.username.contains(query) |
                User.telegram_id.cast(str).contains(query)
            )
            .order_by(User.created_at.desc())
            .offset(offset).limit(per_page)
        )
        return result.scalars().all()
    
    async def update_user_info(self, user_id: int, **kwargs) -> bool:
        """بروزرسانی اطلاعات کاربر"""
        user = await self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def set_user_admin(self, user_id: int, is_admin: bool = True) -> bool:
        """تعیین کاربر به عنوان ادمین"""
        return await self.update_user_info(user_id, is_admin=is_admin)
    
    async def set_user_agent(self, user_id: int, is_agent: bool = True) -> bool:
        """تعیین کاربر به عنوان نماینده"""
        return await self.update_user_info(user_id, is_agent=is_agent)
    
    async def block_user(self, user_id: int) -> bool:
        """مسدود کردن کاربر"""
        return await self.update_user_info(user_id, is_blocked=True, is_active=False)
    
    async def unblock_user(self, user_id: int) -> bool:
        """رفع مسدودی کاربر"""
        return await self.update_user_info(user_id, is_blocked=False, is_active=True)
    
    async def get_users_count(self) -> int:
        """دریافت تعداد کل کاربران"""
        result = await self.db.execute(select(func.count(User.id)))
        return result.scalar_one()
    
    async def get_active_users_count(self) -> int:
        """دریافت تعداد کاربران فعال"""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        return result.scalar_one()
    
    async def get_admin_users_count(self) -> int:
        """دریافت تعداد کاربران ادمین"""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_admin == True)
        )
        return result.scalar_one()
    
    async def get_blocked_users_count(self) -> int:
        """دریافت تعداد کاربران مسدود شده"""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_blocked == True)
        )
        return result.scalar_one()

# نمونه استفاده
# user_manager = UserManager(db_session)
# user = await user_manager.create_user(123456789, "John", "Doe")
