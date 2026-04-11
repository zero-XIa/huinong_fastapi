from fastapi import FastAPI
from contextlib import asynccontextmanager # 导入上下文管理器
from app.db.base import Base
from app.db.session import engine
from app.api.api_v1 import api_router
from fastapi.middleware.cors import CORSMiddleware
# 重要：必须在这里导入所有 model，否则 Base 找不到表结构
from app.models.user import User
from app.models.crop import Crop, Identification, Message


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

# 注册路由（必须在 CORS 中间件之前）
app.include_router(api_router)

# CORS策略拦截（必须在路由注册之后）
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