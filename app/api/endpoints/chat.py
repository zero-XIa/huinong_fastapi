from fastapi import APIRouter, UploadFile, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
import httpx
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/chat")
async def chat(
    username: str = Form(...),
    content: str = Form(...),
    file: UploadFile = None,
    db: AsyncSession = Depends(get_db)
):
    # 保存图片到本地
    image_path = None
    if file:
        user_dir = os.path.join(UPLOAD_DIR, username)
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_path = f"{username}/{file.filename}"
    
    # 上传图片到 Dify
    file_id = None
    if file:
        try:
            file.file.seek(0)
            content_type = file.content_type or f"image/{file.filename.split('.')[-1]}"
            files = {"file": (file.filename, file.file, content_type)}
            data = {"user": username}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.DIFY_API_BASE_URL}/files/upload",
                    headers={"Authorization": f"Bearer {settings.DIFY_API_KEY}"},
                    files=files,
                    data=data
                )
                
                if response.status_code in [200, 201]:
                    file_id = response.json().get("id")
        except Exception as e:
            print(f"上传图片失败: {e}")
    
    # 调用 Dify API
    try:
        request_data = {
            "inputs": {},
            "query": content,
            "response_mode": "blocking",
            "user": username
        }
        
        if file_id:
            request_data["files"] = [{
                "type": "image",
                "transfer_method": "local_file",
                "file_id": file_id
            }]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.DIFY_API_BASE_URL}/chat-messages",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_data,
                timeout=60.0
            )
            
            if response.status_code != 200:
                return {"error": f"Dify API 错误: {response.status_code}"}
            
            result = response.json()
            answer = result.get("answer", "")
            
            return {"message": "后端连通成功！", "data": result}
            
    except Exception as e:
        return {"error": str(e)}
