import time
import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import crud_crop
from app.schemas.crop import IdentifyResponse

from sqlalchemy import select
from app.models.crop import Identification
from typing import List

router = APIRouter()

# 存储路径
UPLOAD_DIR = "uploads"

@router.post("/identify", response_model=IdentifyResponse)
async def identify_disease(
    user_id: int = Form(...), # 接收表单中的用户ID
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    start_time = time.time()
    
    # 1. 物理保存图片：将文件存入本地 uploads 文件夹
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. 模拟 LLM 诊断逻辑 (对应时序图中的提示词工程处理)
    # 这里以后会改为调用大模型 API
    mock_result = {
        "disease_name": "水稻稻瘟病",
        "advice": "建议喷施三环唑，并加强田间水分管理，避免氮肥过量。",
        "confidence": 0.98
    }
    
    # 3. 计算耗时并存入数据库 (数据持久化)
    duration = int((time.time() - start_time) * 1000)
    await crud_crop.create_identification(
        db=db,
        user_id=user_id,
        image_url=file_path,
        disease_result=mock_result,
        duration=duration
    )
    
    return mock_result

@router.get("/history/{user_id}", response_model=List[IdentifyResponse])
async def get_history(user_id: int, db: AsyncSession = Depends(get_db)):
    # 查询该用户的所有识别记录，按时间倒序排列
    result = await db.execute(
        select(Identification)
        .filter(Identification.user_id == user_id)
        .order_by(Identification.create_time.desc())
    )
    history = result.scalars().all()
    
    # 将模型对象转换为 Schema 要求的格式返回
    return [
        {
            "disease_name": item.disease_name,
            "advice": item.advice,
            "confidence": item.confidence,
            "create_time": item.create_time # 如果 Schema 里加了时间字段的话
        } for item in history
    ]