from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crop import Identification
from datetime import datetime

async def create_identification(
    db: AsyncSession, 
    user_id: int, 
    image_url: str, 
    disease_result: dict,
    duration: int
):
    db_obj = Identification(
        user_id=user_id,
        crop_id=1,  # 现阶段默认关联分类ID为1的作物
        image_url=image_url,
        disease_name=disease_result["disease_name"],
        advice=disease_result["advice"],
        confidence=disease_result["confidence"],
        duration=duration
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj