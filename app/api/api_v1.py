from fastapi import APIRouter
from app.api.endpoints import users, crops, news

api_router = APIRouter()
# 赋予前缀，方便版本管理
api_router.include_router(users.router, prefix="/users", tags=["用户模块"])
api_router.include_router(crops.router, prefix="/crops", tags=["作物识别"])
api_router.include_router(news.router, prefix="/news", tags=["农业资讯"])