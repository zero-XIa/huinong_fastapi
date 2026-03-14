from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.news import News
from app.schemas.news import NewsCreate

async def get_news_list(db: AsyncSession, skip: int = 0, limit: int = 10):
    # 分页查询逻辑
    result = await db.execute(
        select(News).order_by(News.publish_time.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_news_detail(db: AsyncSession, news_id: int):

    # 执行更新操作
    await db.execute(
        update(News).where(News.id == news_id).values(view_count=News.view_count + 1)
    )
    # 提交事务，数据写入数据库
    await db.commit()

    # 重新查询最新数据返回
    result = await db.execute(select(News).filter(News.id == news_id))
    return result.scalars().first()

async def create_news(db: AsyncSession, obj_in: NewsCreate):
    db_obj = News(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj