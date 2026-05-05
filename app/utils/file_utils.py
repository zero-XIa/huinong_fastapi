from fastapi import UploadFile, HTTPException
import os
import uuid

# 校验图片文件
def validate_image_file(file: UploadFile) -> bytes:
    # 校验文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={"code": 40001, "message": "请上传 jpg 或 png 格式的图片文件"}
        )
    
    # 读取文件内容
    file_content = file.file.read()
    
    # 校验文件大小（≤10MB）
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail={"code": 40001, "message": "图片大小不能超过 10MB"}
        )
    
    return file_content

# 保存上传的文件
def save_upload_file(file: UploadFile, file_content: bytes) -> str:
    try:
        upload_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "uploads"
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, file_name)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 构建图片 URL
        image_url = f"/uploads/{file_name}"
        return image_url
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": 50002, "message": "上传失败"}
        )
