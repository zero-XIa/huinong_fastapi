import httpx
import traceback
from typing import Optional, Tuple
from app.core.config import settings


# 上传图片到 Dify 的临时文件存储，拿到一个 file_id 供后续工作流使用
async def upload_file_to_dify(file_content: bytes, file_name: str, user_id: str, api_key: str = None) -> str:
    key = api_key or settings.DIFY_API_KEY
    print(f"[dify] 开始上传文件: file_name={file_name}, user_id={user_id}")

    url = f"{settings.DIFY_API_BASE_URL}/files/upload"
    headers = {
        "Authorization": f"Bearer {key}"
    }

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
    except httpx.ReadTimeout:
        print(f"[dify] 文件上传请求超时")
        print(traceback.format_exc())
        raise
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


# 调用 Dify 的对话型应用（/chat-messages），支持传图片和对话上下文
# 返回 (answer文本, conversation_id)
# conversation_id 不为空时表示继续之前对话，为空时开启新会话
async def call_dify_workflow(query: str, conversation_id: Optional[str], user_id: str, file_id: Optional[str] = None, api_key: str = None) -> Tuple[str, str]:
    key = api_key or settings.DIFY_API_KEY
    print(f"[dify] 开始调用工作流: query={query[:50]}..., conversation_id={conversation_id}, user_id={user_id}, file_id={file_id}")
    print(f"[dify] 配置: base_url={settings.DIFY_API_BASE_URL}, api_key={key[:10]}...")

    url = f"{settings.DIFY_API_BASE_URL}/chat-messages"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "user": user_id
    }
    if conversation_id:
        data["conversation_id"] = conversation_id

    if file_id:
        data["files"] = [{
            "type": "image",
            "transfer_method": "local_file",
            "upload_file_id": file_id
        }]

    print(f"[dify] 请求数据: {data}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=55.0)
            print(f"[dify] 响应状态码: {response.status_code}")
            print(f"[dify] 响应内容: {response.text[:200]}...")
            response.raise_for_status()
            result = response.json()

            event = result.get("event")
            if event != "message":
                raise Exception(f"Dify 返回异常事件: {event}")
            answer = result.get("answer", "")
            new_conversation_id = result.get("conversation_id", "")

            print(f"[dify] 调用成功: answer={answer[:50]}..., new_conversation_id={new_conversation_id}")
            return answer, new_conversation_id
    except httpx.ReadTimeout:
        print(f"[dify] 请求超时")
        print(traceback.format_exc())
        raise
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


# 调用病害识别专用的纯 Workflow（/workflows/run），每次独立运行不带对话上下文
# 返回 outputs 字典，已是解析好的 dict 而不是 JSON 字符串
# 注意：纯 Workflow 的文件输入变量必须传在 inputs 里，没有顶层 files 字段
async def call_dify_identify_workflow(
    user_id: str,
    file_id: str,
    api_key: str = None
) -> dict:
    key = api_key or settings.DIFY_API_KEY
    print(f"[dify-identify] 调用 Workflow: user_id={user_id}, file_id={file_id}")

    url = f"{settings.DIFY_API_BASE_URL}/workflows/run"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    # 纯 Workflow 的 inputs 直接填工作流里定义的变量名（如 "image"）
    inputs = {}
    if file_id:
        inputs["image"] = {
            "transfer_method": "local_file",
            "upload_file_id": file_id,
            "type": "image"
        }
    data = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": user_id
    }

    print(f"[dify-identify] 请求数据: {data}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=55.0)
            print(f"[dify-identify] 响应状态码: {response.status_code}")
            print(f"[dify-identify] 响应内容: {response.text[:200]}...")
            response.raise_for_status()
            result = response.json()
            outputs = result.get("data", {}).get("outputs", {})
            print(f"[dify-identify] 识别完成: outputs={outputs}")
            return outputs
    except httpx.ReadTimeout:
        print(f"[dify-identify] 请求超时")
        print(traceback.format_exc())
        raise
    except httpx.RequestError as e:
        print(f"[dify-identify] 请求错误: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise
    except httpx.HTTPStatusError as e:
        print(f"[dify-identify] HTTP 错误: {e.response.status_code}: {e.response.text}")
        print(traceback.format_exc())
        raise
    except Exception as e:
        print(f"[dify-identify] 其他错误: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise
