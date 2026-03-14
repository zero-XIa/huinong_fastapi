# 慧农平台后端接口文档 (v1.0)

**Base URL**: `http://<server-ip>:8000/api/v1`
**数据格式**: `Content-Type: application/json`

---
## 1. 用户管理模块 (Users)

### 1.1 用户注册

- **接口**: `POST /users/register`
- **功能**: 创建新用户账号。
- **请求参数**:

    ```json
    {
      "username": "string",
      "password": "string",
      "email": "string (可选)"
    }
    ```
 
- **返回示例 (200 OK)**:
    ```json
    {
      "id": 1,
      "username": "user123",
      "is_active": true
    }
    ```

### 1.2 用户登录

- **接口**: `POST /users/login`
    
- **功能**: 验证用户凭据并获取用户 ID。
    
- **请求参数**: `Form Data (username, password)`
    
- **返回示例 (200 OK)**:
    
    JSON
    
    ```
    {
      "id": 1,
      "username": "user123",
      "status": "success"
    }
    ```
    

---

## 2. 作物识别模块 (Crops)

### 2.1 上传并识别病害

- **接口**: `POST /crops/identify`
    
- **功能**: 上传图片进行 AI 诊断，并将结果持久化。
    
- **请求参数**: `Multipart/Form-data`
    
    - `user_id`: Integer (用户 ID)
        
    - `file`: File (图片文件)
        
- **返回示例 (200 OK)**:
    
    JSON
    
    ```
    {
      "disease_name": "水稻稻瘟病",
      "advice": "建议喷施三环唑...",
      "confidence": 0.98
    }
    ```
    

### 2.2 获取识别历史记录

- **接口**: `GET /crops/history/{user_id}`
    
- **功能**: 获取指定用户的所有识别记录，按时间倒序排列。
    
- **返回示例 (200 OK)**:
    
    JSON
    
    ```
    [
      {
        "disease_name": "水稻稻瘟病",
        "advice": "建议...",
        "confidence": 0.98,
        "create_time": "2026-03-14T15:00:00"
      }
    ]
    ```
    

---

## 3. 农业资讯模块 (News)

### 3.1 分页获取资讯列表

- **接口**: `GET /news/`
    
- **功能**: 获取首页资讯卡片信息。
    
- **Query 参数**:
    
    - `skip`: Integer (默认 0, 跳过的记录数)
        
    - `limit`: Integer (默认 10, 每页获取条数)
        
- **返回示例 (200 OK)**:
    
    JSON
    
    ```
    [
      {
        "id": 1,
        "title": "2026年春耕补贴",
        "category": "政策",
        "cover_url": "http://...",
        "publish_time": "2026-03-14T10:00:00",
        "view_count": 15
      }
    ]
    ```
    

### 3.2 获取资讯详情

- **接口**: `GET /news/{id}`
    
- **功能**: 获取资讯完整正文，并自动增加阅读量。
    
- **返回示例 (200 OK)**:
    
    JSON
    
    ```
    {
      "id": 1,
      "title": "2026年春耕补贴",
      "content": "这里是详细的 Markdown 或 HTML 正文...",
      "category": "政策",
      "view_count": 16
    }
    ```
    

---

## 4. 智能问答模块 (Chat)

### 4.1 实时对话流

- **接口**: `WSS /ws/chat/{user_id}`
    
- **功能**: 基于 WebSocket 的流式打字机效果对话。
    
- **发送报文**:
    
    JSON
    
    ```
    { "content": "水稻叶子发黄怎么办？" }
    ```
    
- **接收报文 (逐字返回)**:
    
    JSON
    
    ```
    {
      "role": "ai",
      "content": "水",
      "is_end": false
    }
    ```
    

---

## 状态码说明

|**状态码**|**描述**|
|---|---|
|**200**|请求成功。|
|**400**|参数错误或业务逻辑校验失败。|
|**404**|资源未找到（如资讯 ID 不存在）。|
|**500**|服务器内部错误（通常是数据库连接或未处理的异常）。|

---

**下一步建议**：

既然接口文档已经规范化，你可以直接在 Flutter 中根据这些 **JSON 结构** 来定义你的模型类（Model Class）。

**需要我为你提供一个 Flutter (Dart) 调用资讯列表接口的具体 Dio 代码示例吗？**