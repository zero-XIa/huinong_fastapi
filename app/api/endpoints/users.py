from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import crud_user
from app.schemas.user import UserCreate, UserOut, UserLogin

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. 检查用户是否存在
    user = await crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="用户名已被注册")
    # 2. 创建用户
    return await crud_user.create_user(db, user_in)

@router.post("/login")
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_username(db, username=user_in.username)
    if not user or user.password != user_in.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"message": "登录成功", "user_id": user.id, "username": user.username}