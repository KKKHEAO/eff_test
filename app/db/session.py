from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from redis.asyncio import Redis
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def get_redis() -> Redis:
    return redis_client