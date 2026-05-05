from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import crud_news
from app.schemas.news import NewsCreate
from app.api.deps import get_current_user
from app.models.user import User
router = APIRouter()


def _news_to_dict(news) -> dict:
    return {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "category": news.category,
        "cover_url": news.cover_url,
        "publish_time": news.publish_time.isoformat() + "Z",
        "view_count": news.view_count,
    }


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
            "list": [_news_to_dict(n) for n in news_list]
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
        "data": _news_to_dict(news)
    }


@router.post("/")
async def add_news(obj_in: NewsCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": 40301, "message": "角色不匹配"})
    news = await crud_news.create_news(db, obj_in=obj_in)
    return {
        "code": 200,
        "message": "success",
        "data": _news_to_dict(news)
    }


@router.put("/{id}")
async def update_news(id: int, obj_in: NewsCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": 40301, "message": "角色不匹配"})
    news = await crud_news.update_news(db, news_id=id, obj_in=obj_in)
    if not news:
        raise HTTPException(status_code=404, detail={"code": 40404, "message": "资讯不存在"})
    return {
        "code": 200,
        "message": "success",
        "data": _news_to_dict(news)
    }


@router.delete("/{id}")
async def delete_news(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
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
