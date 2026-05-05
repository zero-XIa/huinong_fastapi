from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.api_v1 import api_router
from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.models.user import User
from app.models.identification import Identification
from app.models.message import Message
from app.models.news import News


# 定义生命周期逻辑
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 【启动时执行】: 相当于之前的 on_event("startup")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表同步完成！")
    
    yield  # 这里是分割线，yield 之前是启动逻辑，之后是关闭逻辑
    
    # 【关闭时执行】: 相当于之前的 on_event("shutdown")
    await engine.dispose()
    print("数据库连接已释放")

# 初始化 FastAPI 并注入 lifespan
app = FastAPI(title="HUINONG 后端系统", lifespan=lifespan)

# 注册异常处理器
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 注册路由
app.include_router(api_router)

# 挂载静态文件目录（本地图片访问）
import os
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# CORS策略拦截
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 现阶段允许所有来源，方便调试
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def welcome():
    return {"message": "Huinong API is running!"}