from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# 创建异步引擎：echo=True 可以在终端看到生成的 SQL 语句
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True  # 自动检测并重连断开的连接
)

# 创建异步 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# FastAPI 依赖注入：确保每个请求都有独立的数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session