from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# 注册请求
class UserCreate(BaseModel):
    username: str
    password: str
    phone: Optional[str] = None

# 登录请求
class UserLogin(BaseModel):
    username: str
    password: str

# 更新请求
class UserUpdate(BaseModel):
    phone: Optional[str] = None
    elder_mode: Optional[bool] = None

# 密码更新请求
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# 响应模型（隐藏密码字段）
class UserOut(BaseModel):
    id: int
    username: str
    phone: Optional[str] = None
    elder_mode: bool
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)