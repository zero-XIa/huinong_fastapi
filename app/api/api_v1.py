from fastapi import APIRouter
from app.api.endpoints import users, news, chat, identification

api_router = APIRouter(prefix="/api/v1")
# 赋予前缀，方便版本管理
api_router.include_router(users.router, prefix="/users", tags=["用户模块"])
api_router.include_router(identification.router, prefix="/crops", tags=["病害识别"])
api_router.include_router(news.router, prefix="/news", tags=["农业资讯"])
api_router.include_router(chat.router, prefix="", tags=["问答模块"])
