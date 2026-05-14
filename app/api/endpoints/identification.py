import time

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.crud_identification import create_identification, get_identification, get_identifications, delete_identification, count_identifications
from app.schemas.identification import IdentificationCreate
from app.api.deps import get_current_user
from app.models.user import User
from app.core.config import settings
from app.utils.file_utils import validate_image_file, save_upload_file
from app.utils.dify_client import upload_file_to_dify, call_dify_identify_workflow

router = APIRouter()


# 把 datetime 转成 ISO 8601 格式给前端用
def _format_time(dt):
    return dt.isoformat() + "Z" if dt else None


# 上传图片 -> 保存到本地 -> 送 Dify 识别 -> 解析结果 -> 存数据库
@router.post("/identify")
async def identify_crop(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(f"[identification] 收到病害识别请求: file={file.filename}, user_id={current_user.id}")

    # 校验图片格式(jpg/png)和大小(≤10MB)
    try:
        file_content = await validate_image_file(file)
        print(f"[identification] 文件校验成功: {file.filename}")
    except Exception as e:
        print(f"[identification] 文件校验失败: {e}")
        raise

    # 把图片存到本地 uploads/ 目录，返回可访问的 URL
    image_url = save_upload_file(file, file_content)
    print(f"[identification] 文件保存成功: {image_url}")

    # 送 Dify 做识别
    try:
        # 先把图片上传到 Dify 拿 file_id，后面工作流才能读到这张图
        upload_file_id = await upload_file_to_dify(
            file_content, file.filename, str(current_user.id),
            api_key=settings.DIFY_IDENTIFY_API_KEY
        )
        print(f"[identification] 文件上传到 Dify 成功: {upload_file_id}")

        # 调用病害识别专用 Workflow（/workflows/run），返回的 outputs 已经是 dict
        start_time = time.time()
        outputs = await call_dify_identify_workflow(
            user_id=str(current_user.id),
            file_id=upload_file_id,
            api_key=settings.DIFY_IDENTIFY_API_KEY
        )
        duration = int((time.time() - start_time) * 1000)
        print(f"[identification] Dify Workflow 调用成功，耗时: {duration}ms")

        # 字段为空时用默认值兜底，保证前端和 DB 不会拿到空值
        crop_name = outputs.get("crop_name") or "未知作物"
        disease_name = outputs.get("disease_name") or "未知病害"
        characteristics = outputs.get("characteristics") or "无"
        confidence = outputs.get("confidence", 0.0)

        print(f"[identification] 识别结果: 作物={crop_name}, 病害={disease_name}, 置信度={confidence}")
    except Exception as e:
        print(f"[identification] Dify 调用失败: {e}")
        raise HTTPException(status_code=500, detail={"code": 50003, "message": "识别失败"})

    # 把识别结果写进 tb_identification 表
    identification_in = IdentificationCreate(
        image_url=image_url,
        crop_name=crop_name,
        disease_name=disease_name,
        characteristics=characteristics,
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
            "characteristics": db_identification.characteristics,
            "confidence": db_identification.confidence,
            "duration": db_identification.duration,
            "create_time": _format_time(db_identification.create_time)
        }
    }


# 分页查询当前用户的识别历史（按时间倒序）
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


# 查看某条识别记录的完整详情
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
            "characteristics": identification.characteristics,
            "confidence": identification.confidence,
            "duration": identification.duration,
            "create_time": _format_time(identification.create_time)
        }
    }


# 删除某条识别记录（软删除没做，直接物理删了）
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
