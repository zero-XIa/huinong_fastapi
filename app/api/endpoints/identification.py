from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.crud_identification import create_identification, get_identification, get_identifications, delete_identification, count_identifications
from app.schemas.identification import IdentificationCreate
from app.api.deps import get_current_user
from app.models.user import User
from app.utils.file_utils import validate_image_file, save_upload_file
from app.utils.dify_client import upload_file_to_dify, call_dify_workflow
import time

router = APIRouter()


def _format_time(dt):
    return dt.isoformat() + "Z" if dt else None


@router.post("/identify")
async def identify_crop(
    file: UploadFile = File(...),
    crop_name: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(f"[identification] 收到病害识别请求: file={file.filename}, crop_name={crop_name}, user_id={current_user.id}")
    
    # 校验并读取文件
    try:
        file_content = await validate_image_file(file)
        print(f"[identification] 文件校验成功: {file.filename}")
    except Exception as e:
        print(f"[identification] 文件校验失败: {e}")
        raise
    
    # 保存图片到本地
    image_url = save_upload_file(file, file_content)
    print(f"[identification] 文件保存成功: {image_url}")
    
    # 调用 Dify 识别
    try:
        # 上传文件到 Dify
        upload_file_id = await upload_file_to_dify(file_content, file.filename, str(current_user.id))
        print(f"[identification] 文件上传到 Dify 成功: {upload_file_id}")
        
        # 构造查询
        query = "识别病害"
        
        # 调用 Dify 工作流
        start_time = time.time()
        answer, _ = await call_dify_workflow(
            query=query,
            conversation_id=None,
            user_id=str(current_user.id),
            file_id=upload_file_id
        )
        duration = int((time.time() - start_time) * 1000)
        print(f"[identification] Dify 工作流调用成功，耗时: {duration}ms")
        
        # 解析返回结果
        disease_name = "未知病害"
        confidence = 0.0
        advice = answer
        
        # 尝试从返回结果中提取信息（假设格式为：病害名称：xxx\n置信度：0.95\n防治建议：xxx）
        lines = answer.split('\n')
        for line in lines:
            if line.startswith('病害名称：'):
                disease_name = line.split('：', 1)[1].strip()
            elif line.startswith('置信度：'):
                try:
                    confidence = float(line.split('：', 1)[1].strip())
                except ValueError:
                    pass
        
        print(f"[identification] 识别结果: 病害={disease_name}, 置信度={confidence}")
    except Exception as e:
        print(f"[identification] Dify 调用失败: {e}")
        raise HTTPException(status_code=500, detail={"code": 50003, "message": "识别失败"})
    
    # 保存识别结果
    identification_in = IdentificationCreate(
        image_url=image_url,
        crop_name=crop_name,
        disease_name=disease_name,
        advice=advice,
        confidence=confidence,
        duration=duration
    )
    
    db_identification = await create_identification(db, current_user.id, identification_in)
    print(f"[identification] 识别记录保存成功: id={db_identification.id}")
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": db_identification.id,
            "image_url": db_identification.image_url,
            "crop_name": db_identification.crop_name,
            "disease_name": db_identification.disease_name,
            "advice": db_identification.advice,
            "confidence": db_identification.confidence,
            "duration": db_identification.duration,
            "create_time": _format_time(db_identification.create_time)
        }
    }

@router.get("/history")
async def get_identification_history(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    identifications = await get_identifications(db, current_user.id, skip, limit)
    total = await count_identifications(db, current_user.id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "list": [
                {
                    "id": ident.id,
                    "image_url": ident.image_url,
                    "crop_name": ident.crop_name,
                    "disease_name": ident.disease_name,
                    "confidence": ident.confidence,
                    "create_time": _format_time(ident.create_time)
                }
                for ident in identifications
            ]
        }
    }

@router.get("/history/{id}")
async def get_identification_detail(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    identification = await get_identification(db, id, current_user.id)
    if not identification:
        raise HTTPException(status_code=404, detail={"code": 40404, "message": "记录不存在"})
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": identification.id,
            "user_id": identification.user_id,
            "image_url": identification.image_url,
            "crop_name": identification.crop_name,
            "disease_name": identification.disease_name,
            "advice": identification.advice,
            "confidence": identification.confidence,
            "duration": identification.duration,
            "create_time": _format_time(identification.create_time)
        }
    }

@router.delete("/history/{id}")
async def delete_identification_record(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = await delete_identification(db, id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail={"code": 40404, "message": "记录不存在"})
    return {"code": 200, "message": "success", "data": None}
