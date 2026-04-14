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
    return {"message": "后端连通成功！", "data": {"answer": content}}
