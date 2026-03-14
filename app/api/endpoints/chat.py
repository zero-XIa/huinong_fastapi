from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter()

@router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # 1. 建立与 Flutter 前端的连接
    await websocket.accept()
    
    try:
        while True:
            # 接收前端发送的消息（对应功能模块图中的多模态问题输入）
            data = await websocket.receive_text()
            user_msg = json.loads(data)
            
            # 2. 模拟调用大模型 WSS 接口并实现流式回复
            # 实际开发时，你会在这里通过 websockets 库连接大模型 API
            full_response = "根据您的描述，这可能是由于连日阴雨导致的水稻纹枯病。建议：1. 及时排水晒田；2. 使用井冈霉素进行防治。"
            
            # 模拟“打字机”效果：将回复拆分成字符流发送
            for char in full_response:
                await websocket.send_json({
                    "role": "ai",
                    "content": char,
                    "is_end": False
                })
                await asyncio.sleep(0.05)  # 模拟网络延迟和打字节奏
            
            # 发送结束标识
            await websocket.send_json({"role": "ai", "content": "", "is_end": True})
            
            # 3. TODO: 将完整的对话存入 tb_message 表（对应 E-R 图中的问答消息存证）

    except WebSocketDisconnect:
        print(f"用户 {user_id} 已断开连接")