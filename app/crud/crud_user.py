from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

# 根据用户名查找用户
async def get_user_by_username(db: AsyncSession, username: str):
    # 使用更灵活的查询方式，只查询必要的字段
    from sqlalchemy import text
    query = text("SELECT id, username, password, phone FROM tb_user WHERE username = :username")
    result = await db.execute(query, {"username": username})
    row = result.fetchone()
    if not row:
        return None
    # 创建用户对象，设置默认值
    user = User(
        id=row.id,
        username=row.username,
        password=row.password,
        phone=row.phone,
        elder_mode=False,
        role='user'
    )
    return user

# 根据 ID 查找用户
async def get_user_by_id(db: AsyncSession, user_id: int):
    # 使用更灵活的查询方式，只查询必要的字段
    from sqlalchemy import text
    query = text("SELECT id, username, password, phone FROM tb_user WHERE id = :user_id")
    result = await db.execute(query, {"user_id": user_id})
    row = result.fetchone()
    if not row:
        return None
    # 创建用户对象，设置默认值
    user = User(
        id=row.id,
        username=row.username,
        password=row.password,
        phone=row.phone,
        elder_mode=False,
        role='user'
    )
    return user

# 创建新用户
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