from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import crud_user
from app.schemas.user import UserCreate, UserOut, UserLogin, UserUpdate, PasswordUpdate
from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User

router = APIRouter()

@router.post("/register")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. 检查用户是否存在
    user = await crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="用户名已被注册")
    # 2. 创建用户
    db_user = await crud_user.create_user(db, user_in)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": db_user.id,
            "username": db_user.username,
            "phone": db_user.phone,
            "elder_mode": db_user.elder_mode,
            "role": db_user.role,
            "create_time": db_user.create_time.isoformat() if db_user.create_time else None
        }
    }

@router.post("/login")
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_username(db, username=user_in.username)
    if not user or not verify_password(user_in.password, user.password):
        raise HTTPException(
            status_code=401,
            detail={"code": 40101, "message": "用户名或密码错误"}
        )
    user_role = getattr(user, 'role', 'user')
    access_token = create_access_token(data={"sub": str(user.id), "role": user_role})
    return {
        "code": 200,
        "message": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "elder_mode": getattr(user, 'elder_mode', False),
                "role": user_role,
                "create_time": user.create_time.isoformat() if user.create_time else None
            }
        }
    }

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "phone": getattr(current_user, 'phone', None),
            "elder_mode": getattr(current_user, 'elder_mode', False),
            "role": getattr(current_user, 'role', 'user'),
            "create_time": current_user.create_time.isoformat() if current_user.create_time else None
        }
    }

@router.put("/me")
async def update_current_user_info(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await db.merge(current_user)
    if user_update.phone:
        user.phone = user_update.phone
    if user_update.elder_mode is not None:
        user.elder_mode = user_update.elder_mode
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "elder_mode": user.elder_mode,
            "role": user.role,
            "create_time": user.create_time.isoformat() if user.create_time else None
        }
    }

@router.put("/password")
async def update_password(
    password_update: PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(password_update.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")

    user = await db.merge(current_user)
    user.password = hash_password(password_update.new_password)
    
    await db.commit()
    
    return {
        "code": 200,
        "message": "success",
        "data": None
    }

@router.get("/admin/users")
async def get_admin_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查管理员权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": 40301, "message": "角色不匹配"})
    
    # 模拟返回用户列表
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": [
                {
                    "id": 1,
                    "username": "admin",
                    "phone": "13800138000",
                    "role": "admin",
                    "create_time": "2024-01-01 12:00:00"
                }
            ]
        }
    }