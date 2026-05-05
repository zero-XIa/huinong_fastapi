from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        description="用户名，3-50位，只允许字母、数字、下划线"
    )
    password: str = Field(
        min_length=8,
        max_length=20,
        description="密码，8-20位，必须包含字母和数字"
    )
    phone: Optional[str] = Field(
        default=None,
        description="手机号，11位数字以1开头"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("用户名只允许字母、数字、下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[a-zA-Z]", v) or not re.search(r"\d", v):
            raise ValueError("密码必须包含字母和数字")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^1\d{10}$", v):
            raise ValueError("手机号格式不正确")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    phone: Optional[str] = Field(default=None)
    elder_mode: Optional[bool] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^1\d{10}$", v):
            raise ValueError("手机号格式不正确")
        return v


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(
        min_length=8,
        max_length=20,
        description="新密码，8-20位，必须包含字母和数字"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not re.search(r"[a-zA-Z]", v) or not re.search(r"\d", v):
            raise ValueError("密码必须包含字母和数字")
        return v


class UserOut(BaseModel):
    id: int
    username: str
    phone: Optional[str] = None
    elder_mode: bool
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)
