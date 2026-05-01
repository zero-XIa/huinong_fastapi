from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from app.models.news import News
from app.schemas.news import NewsCreate

async def get_news_list(db: AsyncSession, skip: int = 0, limit: int = 10):
    query = text("SELECT id, title, content, category, cover_url, publish_time, view_count FROM tb_news WHERE is_deleted = FALSE ORDER BY publish_time DESC LIMIT :limit OFFSET :skip")
    result = await db.execute(query, {"skip": skip, "limit": limit})
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

async def get_news_count(db: AsyncSession):
    query = text("SELECT COUNT(*) AS cnt FROM tb_news WHERE is_deleted = FALSE")
    result = await db.execute(query)
    row = result.fetchone()
    return row._mapping['cnt'] if row else 0

async def get_news_detail(db: AsyncSession, news_id: int):
    # 先更新浏览量
    await db.execute(
        update(News).where(News.id == news_id).values(view_count=News.view_count + 1)
    )
    await db.commit()

    # 查询详情
    query = text("SELECT id, title, content, category, cover_url, publish_time, view_count FROM tb_news WHERE id = :news_id AND is_deleted = FALSE")
    result = await db.execute(query, {"news_id": news_id})
    row = result.fetchone()
    if not row:
        return None
    return dict(row._mapping)

async def create_news(db: AsyncSession, obj_in: NewsCreate):
    query = text("""
        INSERT INTO tb_news (title, content, category, cover_url, publish_time, is_deleted)
        VALUES (:title, :content, :category, :cover_url, NOW(), FALSE)
    """)
    result = await db.execute(query, {
        "title": obj_in.title,
        "content": obj_in.content,
        "category": obj_in.category,
        "cover_url": obj_in.cover_url,
    })
    news_id = result.lastrowid
    await db.commit()
    select_query = text("SELECT id, title, content, category, cover_url, publish_time, view_count FROM tb_news WHERE id = :news_id")
    row = (await db.execute(select_query, {"news_id": news_id})).fetchone()
    return dict(row._mapping) if row else None

async def update_news(db: AsyncSession, news_id: int, obj_in: NewsCreate):
    values = obj_in.model_dump(exclude_unset=True)
    await db.execute(
        update(News).where(News.id == news_id).values(**values)
    )
    await db.commit()
    query = text("SELECT id, title, content, category, cover_url, publish_time, view_count FROM tb_news WHERE id = :news_id AND is_deleted = FALSE")
    row = (await db.execute(query, {"news_id": news_id})).fetchone()
    return dict(row._mapping) if row else None

async def delete_news(db: AsyncSession, news_id: int):
    result = await db.execute(
        update(News).where(News.id == news_id).values(is_deleted=True)
    )
    await db.commit()
    return result.rowcount > 0