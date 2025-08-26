from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from core.settings import settings

DATABASE_URL = settings.db.dsn  # dsn из .env
# Синхронная версия для Celery задач
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Синхронный движок для Celery
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, future=True)
SyncSessionLocal = sessionmaker(sync_engine, class_=Session, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def get_sync_db():
    with SyncSessionLocal() as session:
        yield session

# Временная функция для автосоздания таблиц (только для отладки/старта)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
