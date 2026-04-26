from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime
from app.models.session import Session


async def create_session(db: AsyncSession, user_id: int, session_id: str, title: str) -> Session:
    db_session = Session(
        user_id=user_id,
        session_id=session_id,
        title=title,
        last_message_time=datetime.utcnow()
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session


async def get_session_by_id(db: AsyncSession, session_id: str, user_id: int) -> Session:
    result = await db.execute(
        select(Session).where(
            Session.session_id == session_id,
            Session.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_sessions(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Session], int]:
    # 获取总数
    count_result = await db.execute(
        select(Session).where(Session.user_id == user_id)
    )
    total = len(count_result.scalars().all())
    
    # 获取分页数据
    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.last_message_time.desc())
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()
    return sessions, total


async def update_session_last_message_time(db: AsyncSession, session_id: str) -> None:
    await db.execute(
        update(Session)
        .where(Session.session_id == session_id)
        .values(last_message_time=datetime.utcnow())
    )
    await db.commit()


async def update_session_dify_conversation_id(db: AsyncSession, session_id: str, dify_conversation_id: str) -> None:
    await db.execute(
        update(Session)
        .where(Session.session_id == session_id)
        .values(dify_conversation_id=dify_conversation_id)
    )
    await db.commit()


async def update_session_title(db: AsyncSession, session_id: str, title: str) -> None:
    """更新会话标题"""
    await db.execute(
        update(Session)
        .where(Session.session_id == session_id)
        .values(title=title)
    )
    await db.commit()


async def delete_session(db: AsyncSession, session_id: str, user_id: int) -> bool:
    result = await db.execute(
        delete(Session)
        .where(
            Session.session_id == session_id,
            Session.user_id == user_id
        )
    )
    await db.commit()
    return result.rowcount > 0