from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.crud import crud_news
from app.schemas.news import NewsResponse, NewsCreate

router = APIRouter()

@router.get("/", response_model=List[NewsResponse])
async def read_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await crud_news.get_news_list(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=NewsResponse)
async def read_news_detail(id: int, db: AsyncSession = Depends(get_db)):
    news = await crud_news.get_news_detail(db, news_id=id)
    if not news:
        raise HTTPException(status_code=404, detail="资讯未找到")
    return news

@router.post("/", response_model=NewsResponse)
async def add_news(obj_in: NewsCreate, db: AsyncSession = Depends(get_db)):
    # 实际开发中此处需添加管理员权限校验
    return await crud_news.create_news(db, obj_in=obj_in)