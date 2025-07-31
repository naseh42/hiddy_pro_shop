from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# ایجاد موتور دیتابیس
engine = create_async_engine(
    Config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# ایجاد session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# کلاس پایه برای مدل‌ها
Base = declarative_base()

# توابع کمکی
async def get_db():
    """دریافت session دیتابیس"""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """ایجاد جداول دیتابیس"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """بستن اتصال دیتابیس"""
    await engine.dispose()
