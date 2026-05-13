from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.news import News
from app.schemas.news import NewsCreate


async def get_news_list(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(News)
        .filter(News.is_deleted == False)
        .order_by(News.publish_time.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_news_count(db: AsyncSession):
    result = await db.execute(
        select(func.count()).select_from(News).filter(News.is_deleted == False)
    )
    return result.scalar() or 0


async def get_news_detail(db: AsyncSession, news_id: int):
    await db.execute(
        update(News).where(News.id == news_id).values(view_count=News.view_count + 1)
    )
    await db.commit()

    result = await db.execute(
        select(News).filter(News.id == news_id, News.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def create_news(db: AsyncSession, obj_in: NewsCreate):
    db_news = News(
        title=obj_in.title,
        content=obj_in.content,
        category=obj_in.category,
        cover_url=obj_in.cover_url,
        publish_time=obj_in.publish_time or func.now(),
    )
    db.add(db_news)
    await db.commit()
    await db.refresh(db_news)
    return db_news


async def update_news(db: AsyncSession, news_id: int, obj_in: NewsCreate):
    values = obj_in.model_dump(exclude_unset=True)
    await db.execute(update(News).where(News.id == news_id).values(**values))
    await db.commit()
    result = await db.execute(
        select(News).filter(News.id == news_id, News.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def delete_news(db: AsyncSession, news_id: int):
    result = await db.execute(
        update(News).where(News.id == news_id).values(is_deleted=True)
    )
    await db.commit()
    return result.rowcount > 0
