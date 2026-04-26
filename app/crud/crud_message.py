from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.message import Message


async def create_message(db: AsyncSession, user_id: int, session_id: str, role: str, content: str) -> Message:
    db_message = Message(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(db_message)
    return db_message


async def bulk_create_messages(db: AsyncSession, messages: list[dict]) -> None:
    db_messages = [
        Message(
            user_id=msg['user_id'],
            session_id=msg['session_id'],
            role=msg['role'],
            content=msg['content']
        )
        for msg in messages
    ]
    db.add_all(db_messages)
    await db.commit()


async def get_messages(db: AsyncSession, session_id: str, user_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Message], int]:
    # 获取总数
    count_result = await db.execute(
        select(Message).where(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
    )
    total = len(count_result.scalars().all())
    
    # 获取分页数据
    result = await db.execute(
        select(Message)
        .where(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
        .order_by(Message.create_time.asc())
        .offset(skip)
        .limit(limit)
    )
    messages = result.scalars().all()
    return messages, total


async def delete_messages_by_session(db: AsyncSession, session_id: str, user_id: int) -> None:
    await db.execute(
        delete(Message)
        .where(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
    )
    await db.commit()