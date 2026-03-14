from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate

# 根据用户名查找用户
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

# 创建新用户
async def create_user(db: AsyncSession, user_in: UserCreate):
    # 现阶段直接存储明文（后续建议加哈希加密）
    db_user = User(
        username=user_in.username,
        password=user_in.password,
        phone=user_in.phone
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user