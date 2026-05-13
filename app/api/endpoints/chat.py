from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import os
import httpx
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.crud import crud_session, crud_message
from app.utils.dify_client import call_dify_workflow, upload_file_to_dify
from app.utils.file_utils import validate_image_file, save_upload_file

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def _cleanup_upload_file(image_url: str):
    try:
        file_name = image_url.lstrip("/uploads/")
        file_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[chat] 孤儿文件已清理: {file_path}")
    except Exception:
        pass


@router.post("/chat/message")
async def chat_message(
    content: str = Form(...),
    session_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # [修复] 去除 session_id 首尾空格
    if session_id:
        session_id = session_id.strip()

    print(f"[chat] 收到消息请求: content={content[:50]}..., session_id={session_id}, user_id={current_user.id}")

    # 处理会话 ID
    if not session_id:
        # 生成新会话 ID
        session_id = uuid.uuid4().hex
        # 创建会话记录
        title = content[:20] if len(content) > 20 else content
        await crud_session.create_session(db, user_id=current_user.id, session_id=session_id, title=title)
        dify_conversation_id = None
        print(f"[chat] 创建新会话: session_id={session_id}")
    else:
        # 查询会话
        session = await crud_session.get_session_by_id(db, session_id=session_id, user_id=current_user.id)
        if not session:
            print(f"[chat] 会话不存在: session_id={session_id}")
            raise HTTPException(
                status_code=404,
                detail={"code": 40401, "message": "会话不存在"}
            )
        dify_conversation_id = session.dify_conversation_id
        print(f"[chat] 查询到已有会话: session_id={session_id}, dify_conversation_id={dify_conversation_id}")

    try:
        # 调用 Dify 工作流
        print(f"[chat] 调用 Dify: query={content[:50]}..., conversation_id={dify_conversation_id}")
        answer, new_conversation_id = await call_dify_workflow(
            query=content,
            conversation_id=dify_conversation_id,
            user_id=str(current_user.id)
        )
        print(f"[chat] Dify 调用成功: answer={answer[:50]}..., new_conversation_id={new_conversation_id}")

        # 保存 Dify 会话 ID（如果是新会话）
        if not dify_conversation_id:
            await crud_session.update_session_dify_conversation_id(db, session_id=session_id, dify_conversation_id=new_conversation_id)

        # 保存消息
        messages = [
            {
                "user_id": current_user.id,
                "session_id": session_id,
                "role": "user",
                "content": content
            },
            {
                "user_id": current_user.id,
                "session_id": session_id,
                "role": "ai",
                "content": answer
            }
        ]
        await crud_message.bulk_create_messages(db, messages)

        # 更新会话最后消息时间
        await crud_session.update_session_last_message_time(db, session_id=session_id)

        return {
            "code": 200,
            "message": "success",
            "data": {
                "answer": answer,
                "session_id": session_id
            }
        }
    except Exception as e:
        print(f"[chat] Dify 调用失败: {type(e).__name__}: {e}, session_id={session_id}, user_id={current_user.id}")
        raise HTTPException(
            status_code=500,
            detail={"code": 50003, "message": "AI 服务异常"}
        )


# [修改1: 删除 mock 识别导入]
# [修改2: 统一参数名 text -> content]
@router.post("/chat/message_with_image")
async def chat_message_with_image(
    file: UploadFile,
    content: Optional[str] = Form(None),  # 统一参数名：text -> content
    session_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # [修复] 去除 session_id 首尾空格
    if session_id:
        session_id = session_id.strip()

    print(f"[chat] 收到图片消息请求: file={file.filename}, content={content}, session_id={session_id}, user_id={current_user.id}")

    # 文件校验
    try:
        contents = await validate_image_file(file)
        print(f"[chat] 文件校验成功: {file.filename}")
    except Exception as e:
        print(f"[chat] 文件校验失败: {e}")
        raise

    # 保存图片到本地
    image_url = save_upload_file(file, contents)
    print(f"[chat] 文件保存成功: {image_url}")

    # 处理会话 ID / 新会话标记
    is_new_session = not session_id
    if not session_id:
        session_id = uuid.uuid4().hex
        dify_conversation_id = None
    else:
        session = await crud_session.get_session_by_id(db, session_id=session_id, user_id=current_user.id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail={"code": 40401, "message": "会话不存在"}
            )
        dify_conversation_id = session.dify_conversation_id

    try:
        # 上传文件到 Dify
        upload_file_id = await upload_file_to_dify(contents, file.filename, str(current_user.id))

        # [修改3: 简化 query 构造，直接使用用户输入]
        query = content if content else "请分析上传的图片并给出建议"

        # 调用 Dify 工作流
        answer, new_conversation_id = await call_dify_workflow(
            query=query,
            conversation_id=dify_conversation_id,
            user_id=str(current_user.id),
            file_id=upload_file_id
        )

        # Dify 成功后，创建新会话记录（避免孤儿会话）
        if is_new_session:
            title = "图片问答"
            await crud_session.create_session(db, user_id=current_user.id, session_id=session_id, title=title)

        # 保存 Dify 会话 ID
        if is_new_session:
            await crud_session.update_session_dify_conversation_id(db, session_id=session_id, dify_conversation_id=new_conversation_id)

        # 保存消息
        messages = [
            {
                "user_id": current_user.id,
                "session_id": session_id,
                "role": "user",
                "content": query,
                "image_url": image_url
            },
            {
                "user_id": current_user.id,
                "session_id": session_id,
                "role": "ai",
                "content": answer
            }
        ]
        await crud_message.bulk_create_messages(db, messages)

        # 更新会话最后消息时间
        await crud_session.update_session_last_message_time(db, session_id=session_id)

        return {
            "code": 200,
            "message": "success",
            "data": {
                "answer": answer,
                "session_id": session_id,
                "image_url": image_url
            }
        }
    except httpx.ReadTimeout:
        print(f"[chat] Dify 请求超时: session_id={session_id}, user_id={current_user.id}")
        _cleanup_upload_file(image_url)
        raise HTTPException(
            status_code=500,
            detail={"code": 50003, "message": "图片分析超时，请稍后重试"}
        )
    except Exception as e:
        print(f"[chat] Dify 调用失败: {type(e).__name__}: {e}, session_id={session_id}, user_id={current_user.id}")
        _cleanup_upload_file(image_url)
        raise HTTPException(
            status_code=500,
            detail={"code": 50003, "message": "AI 服务异常，请稍后重试"}
        )


@router.get("/chat/sessions")
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 限制最大查询数量
    limit = min(limit, 100)

    # 查询会话列表
    sessions, total = await crud_session.get_sessions(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    # 构造响应数据
    session_list = [
        {
            "session_id": session.session_id,
            "title": session.title,
            "last_message_time": session.last_message_time.isoformat() + "Z"
        }
        for session in sessions
    ]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "list": session_list
        }
    }


@router.get("/chat/sessions/{session_id}/messages")
async def get_chat_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 限制最大查询数量
    limit = min(limit, 100)

    # 验证会话是否存在
    session = await crud_session.get_session_by_id(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail={"code": 40401, "message": "会话不存在"}
        )

    # 查询消息列表
    messages, total = await crud_message.get_messages(
        db,
        session_id=session_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    # 构造响应数据
    message_list = [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "image_url": message.image_url,
            "create_time": message.create_time.isoformat() + "Z"
        }
        for message in messages
    ]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "list": message_list
        }
    }


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 删除会话相关的消息
    await crud_message.delete_messages_by_session(db, session_id=session_id, user_id=current_user.id)

    # 删除会话
    success = await crud_session.delete_session(db, session_id=session_id, user_id=current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail={"code": 40401, "message": "会话不存在"}
        )

    return {
        "code": 200,
        "message": "success",
        "data": None
    }