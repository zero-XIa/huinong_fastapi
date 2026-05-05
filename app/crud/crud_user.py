from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate):
    hashed_password = hash_password(user_in.password)
    db_user = User(
        username=user_in.username,
        password=hashed_password,
        phone=user_in.phone
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
