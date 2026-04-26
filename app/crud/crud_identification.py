from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func
from app.models.identification import Identification
from app.schemas.identification import IdentificationCreate, IdentificationUpdate
from typing import List, Optional

async def create_identification(db: AsyncSession, user_id: int, identification_in: IdentificationCreate):
    db_identification = Identification(
        user_id=user_id,
        image_url=identification_in.image_url,
        crop_name=identification_in.crop_name,
        disease_name=identification_in.disease_name,
        advice=identification_in.advice,
        confidence=identification_in.confidence,
        duration=identification_in.duration
    )
    db.add(db_identification)
    await db.commit()
    await db.refresh(db_identification)
    return db_identification

async def get_identification(db: AsyncSession, identification_id: int, user_id: int):
    result = await db.execute(
        select(Identification)
        .filter(Identification.id == identification_id)
        .filter(Identification.user_id == user_id)
    )
    return result.scalars().first()

async def get_identifications(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Identification)
        .filter(Identification.user_id == user_id)
        .order_by(Identification.create_time.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def count_identifications(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(func.count(Identification.id))
        .filter(Identification.user_id == user_id)
    )
    return result.scalar()

async def delete_identification(db: AsyncSession, identification_id: int, user_id: int):
    result = await db.execute(
        delete(Identification)
        .filter(Identification.id == identification_id)
        .filter(Identification.user_id == user_id)
    )
    await db.commit()
    return result.rowcount > 0