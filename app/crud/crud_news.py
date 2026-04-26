from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from app.models.news import News
from app.schemas.news import NewsCreate

async def get_news_list(db: AsyncSession, skip: int = 0, limit: int = 10):
    # 分页查询逻辑，使用基础 SQL 查询避免数据库列不一致问题
    query = text("SELECT id, title, content, category, cover_url, publish_time, view_count FROM tb_news ORDER BY publish_time DESC LIMIT :limit OFFSET :skip")
    result = await db.execute(query, {"skip": skip, "limit": limit})
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

async def get_news_detail(db: AsyncSession, news_id: int):
    # 先更新浏览量
    await db.execute(
        update(News).where(News.id == news_id).values(view_count=News.view_count + 1)
    )
    await db.commit()

    # 查询详情
    query = text("SELECT id, title, content, category, cover_url, publish_time, view_count FROM tb_news WHERE id = :news_id")
    result = await db.execute(query, {"news_id": news_id})
    row = result.fetchone()
    if not row:
        return None
    return dict(row._mapping)

async def create_news(db: AsyncSession, obj_in: NewsCreate):
    db_obj = News(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj