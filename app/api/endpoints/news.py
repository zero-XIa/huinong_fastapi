from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.crud import crud_news
from app.schemas.news import NewsResponse, NewsCreate
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def read_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db)
):
    news_list = await crud_news.get_news_list(db, skip=skip, limit=limit)
    total = await crud_news.get_news_count(db)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "list": news_list
        }
    }

@router.get("/{id}")
async def read_news_detail(id: int, db: AsyncSession = Depends(get_db)):
    news = await crud_news.get_news_detail(db, news_id=id)
    if not news:
        raise HTTPException(status_code=404, detail={"code": 40404, "message": "资讯不存在"})
    return {
        "code": 200,
        "message": "success",
        "data": news
    }

@router.post("/")
async def add_news(obj_in: NewsCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查管理员权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": 40301, "message": "角色不匹配"})
    news = await crud_news.create_news(db, obj_in=obj_in)
    return {
        "code": 200,
        "message": "success",
        "data": news
    }

@router.put("/{id}")
async def update_news(id: int, obj_in: NewsCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查管理员权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": 40301, "message": "角色不匹配"})
    news = await crud_news.update_news(db, news_id=id, obj_in=obj_in)
    if not news:
        raise HTTPException(status_code=404, detail={"code": 40404, "message": "资讯不存在"})
    return {
        "code": 200,
        "message": "success",
        "data": news
    }

@router.delete("/{id}")
async def delete_news(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查管理员权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": 40301, "message": "角色不匹配"})
    success = await crud_news.delete_news(db, news_id=id)
    if not success:
        raise HTTPException(status_code=404, detail={"code": 40404, "message": "资讯不存在"})
    return {
        "code": 200,
        "message": "success",
        "data": None
    }