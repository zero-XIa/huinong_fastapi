import httpx
import traceback
from typing import Optional, Tuple
from app.core.config import settings


async def upload_file_to_dify(file_content: bytes, file_name: str, user_id: str) -> str:
    """上传文件到 Dify 并返回 upload_file_id"""
    print(f"[dify] 开始上传文件: file_name={file_name}, user_id={user_id}")
    
    url = f"{settings.DIFY_API_BASE_URL}/files/upload"
    headers = {
        "Authorization": f"Bearer {settings.DIFY_API_KEY}"
    }
    
    # 准备多部分表单数据
    files = {
        "file": (file_name, file_content)
    }
    data = {
        "user": user_id
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, files=files, data=data, timeout=30.0)
            print(f"[dify] 文件上传响应状态码: {response.status_code}")
            print(f"[dify] 文件上传响应内容: {response.text[:200]}...")
            response.raise_for_status()
            result = response.json()
            
            upload_file_id = result.get("id")
            if not upload_file_id:
                print(f"[dify] 上传文件响应完整内容: {result}")
                raise Exception("Dify 返回的文件 ID 为空")
            
            print(f"[dify] 文件上传成功: upload_file_id={upload_file_id}")
            return upload_file_id
    except httpx.RequestError as e:
        print(f"[dify] 文件上传请求错误: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise
    except httpx.HTTPStatusError as e:
        print(f"[dify] 文件上传 HTTP 错误: {e.response.status_code}: {e.response.text}")
        print(traceback.format_exc())
        raise
    except Exception as e:
        print(f"[dify] 文件上传其他错误: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise


async def call_dify_workflow(query: str, conversation_id: Optional[str], user_id: str, file_id: Optional[str] = None) -> Tuple[str, str]:
    print(f"[dify] 开始调用工作流: query={query[:50]}..., conversation_id={conversation_id}, user_id={user_id}, file_id={file_id}")
    print(f"[dify] 配置: base_url={settings.DIFY_API_BASE_URL}, api_key={settings.DIFY_API_KEY[:10]}...")
    
    # 端点 URL 改为 /chat-messages
    url = f"{settings.DIFY_API_BASE_URL}/chat-messages"
    headers = {
        "Authorization": f"Bearer {settings.DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    # 请求体结构：inputs 为空对象，query 为顶层字段
    data = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "user": user_id
    }
    if conversation_id:
        data["conversation_id"] = conversation_id
    
    # 如果有文件 ID，添加 files 数组
    if file_id:
        data["files"] = [{
            "type": "image",
            "transfer_method": "local_file",
            "upload_file_id": file_id
        }]
    
    print(f"[dify] 请求数据: {data}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=30.0)
            print(f"[dify] 响应状态码: {response.status_code}")
            print(f"[dify] 响应内容: {response.text[:200]}...")
            response.raise_for_status()
            result = response.json()
            
            # 响应解析：检查 event 类型，answer 和 conversation_id 是顶层字段
            event = result.get("event")
            if event != "message":
                raise Exception(f"Dify 返回异常事件: {event}")
            answer = result.get("answer", "")
            new_conversation_id = result.get("conversation_id", "")
            
            print(f"[dify] 调用成功: answer={answer[:50]}..., new_conversation_id={new_conversation_id}")
            return answer, new_conversation_id
    except httpx.RequestError as e:
        print(f"[dify] 请求错误: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise
    except httpx.HTTPStatusError as e:
        print(f"[dify] HTTP 错误: {e.response.status_code}: {e.response.text}")
        print(traceback.format_exc())
        raise
    except Exception as e:
        print(f"[dify] 其他错误: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise