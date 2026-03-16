# 慧农平台后端接口文档 (v0.1.0)

**Base URL**: `http://<server-ip>:8000`
**数据格式**: `Content-Type: application/json`

---
## 1. 根路径 (Root)

### 1.1 欢迎接口

- **接口**: `GET /`
- **功能**: 返回欢迎信息。
- **返回示例 (200 OK)**:
    ```json
    {
      "message": "Welcome to HUINONG API"
    }
    ```

---
## 2. 用户管理模块 (Users)

### 2.1 用户注册

- **接口**: `POST /api/v1/users/register`
- **功能**: 创建新用户账号。
- **请求体 (application/json)**:
    ```json
    {
      "username": "string",
      "password": "string",
      "phone": "string (可选)"
    }
    ```
- **返回示例 (200 OK)**:
    ```json
    {
      "id": 1,
      "username": "user123",
      "phone": "13800138000",
      "elder_mode": false,
      "create_time": "2026-03-16T12:00:00Z"
    }
    ```

### 2.2 用户登录

- **接口**: `POST /api/v1/users/login`
- **功能**: 验证用户凭据。
- **请求体 (application/json)**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
- **返回示例 (200 OK)**:
    ```json
    {
      "message": "Login successful"
    }
    ```

---
## 3. 作物识别模块 (Crops)

### 3.1 上传并识别病害

- **接口**: `POST /api/v1/crops/identify`
- **功能**: 上传图片进行 AI 诊断，并将结果持久化。
- **请求参数**: `Multipart/Form-data`
    - `user_id`: Integer (用户 ID)
    - `file`: File (图片文件)
- **返回示例 (200 OK)**:
    ```json
    {
      "disease_name": "水稻稻瘟病",
      "advice": "建议喷施三环唑...",
      "confidence": 0.98
    }
    ```

### 3.2 获取识别历史记录

- **接口**: `GET /api/v1/crops/history/{user_id}`
- **功能**: 获取指定用户的所有识别记录，按时间倒序排列。
- **返回示例 (200 OK)**:
    ```json
    [
      {
        "disease_name": "水稻稻瘟病",
        "advice": "建议...",
        "confidence": 0.98
      }
    ]
    ```

---
## 4. 农业资讯模块 (News)

### 4.1 分页获取资讯列表

- **接口**: `GET /api/v1/news/`
- **功能**: 获取首页资讯卡片信息。
- **Query 参数**:
    - `skip`: Integer (默认 0, 跳过的记录数)
    - `limit`: Integer (默认 10, 每页获取条数)
- **返回示例 (200 OK)**:
    ```json
    [
      {
        "id": 1,
        "title": "2026年春耕补贴",
        "content": "资讯内容摘要...",
        "category": "政策",
        "cover_url": "http://...",
        "publish_time": "2026-03-14T10:00:00",
        "view_count": 15
      }
    ]
    ```

### 4.2 添加资讯

- **接口**: `POST /api/v1/news/`
- **功能**: 创建一条新的农业资讯。
- **请求体 (application/json)**:
    ```json
    {
      "title": "新的资讯标题",
      "content": "新的资讯详细内容...",
      "category": "技术",
      "cover_url": "http://... (可选)"
    }
    ```
- **返回示例 (200 OK)**:
    ```json
    {
        "id": 2,
        "title": "新的资讯标题",
        "content": "新的资讯详细内容...",
        "category": "技术",
        "cover_url": "http://...",
        "publish_time": "2026-03-16T14:00:00",
        "view_count": 0
    }
    ```

### 4.3 获取资讯详情

- **接口**: `GET /api/v1/news/{id}`
- **功能**: 获取资讯完整正文，并自动增加阅读量。
- **返回示例 (200 OK)**:
    ```json
    {
      "id": 1,
      "title": "2026年春耕补贴",
      "content": "这里是详细的 Markdown 或 HTML 正文...",
      "category": "政策",
      "cover_url": "http://...",
      "publish_time": "2026-03-14T10:00:00",
      "view_count": 16
    }
    ```

---
## 5. 智能问答模块 (Chat)

### 5.1 实时对话流

- **接口**: `WSS /ws/chat/{user_id}`
- **功能**: 基于 WebSocket 的流式打字机效果对话。
- **发送报文**:
    ```json
    { "content": "水稻叶子发黄怎么办？" }
    ```
- **接收报文 (逐字返回)**:
    ```json
    {
      "role": "ai",
      "content": "水",
      "is_end": false
    }
    ```

---
## 6. 状态码说明

|**状态码**|**描述**|
|---|---|
|**200**|请求成功。|
|**422**|请求体验证失败 (Unprocessable Entity)。|
|**404**|资源未找到。|
|**500**|服务器内部错误。|

---
## 7. 数据库表设计 (Database Schema)

### 7.1 用户表 (tb_user)

用于存储用户基础凭证、鉴权数据以及全局适老化配置参数。

| **字段名** | **类型** | **长度** | **约束** | **描述** |
|---|---|---|---|---|
| id | INTEGER | - | PRIMARY KEY, AUTOINCREMENT | 用户唯一自增 ID |
| username | VARCHAR | 50 | UNIQUE, NOT NULL | 登录账号 |
| password | VARCHAR | 128 | NOT NULL | 登录密码（加密存储） |
| phone | VARCHAR | 20 | UNIQUE | 用户绑定手机号 |
| elder_mode | BOOLEAN | - | DEFAULT FALSE | 长辈模式开关状态 |
| create_time | DATETIME | - | SERVER_DEFAULT | 账号注册时间 |

### 7.2 资讯表 (tb_news)

用于发布和管理农业相关的政策、预警、农技等资讯内容。

| **字段名** | **类型** | **长度** | **约束** | **描述** |
|---|---|---|---|---|
| id | INTEGER | - | PRIMARY KEY, INDEX | 资讯唯一 ID |
| title | VARCHAR | 200 | NOT NULL | 资讯标题 |
| content | TEXT | - | NOT NULL | 存储 Markdown/HTML |
| category | VARCHAR | 50 | - | 分类 (政策, 预警, 农技等) |
| cover_url | VARCHAR | 500 | - | 封面图地址 |
| publish_time | DATETIME | - | DEFAULT | 发布时间 |
| view_count | INTEGER | - | DEFAULT 0 | 阅读量 |

### 7.3 作物基础信息表 (tb_crop)

用于维护系统后端推理引擎支持的农作物标准库信息。

| **字段名** | **类型** | **长度** | **约束** | **描述** |
|---|---|---|---|---|
| id | INTEGER | - | PRIMARY KEY | 作物分类 ID |
| crop_name | VARCHAR | 50 | NOT NULL | 作物名称（如：水稻、小麦） |
| description | TEXT | - | - | 作物特征简述 |

### 7.4 病害识别记录表 (tb_identification)

持久化存储病害识别业务的流水数据，记录从影像采集到 AI 解析的全过程指标。

| **字段名** | **类型** | **长度** | **约束** | **描述** |
|---|---|---|---|---|
| id | INTEGER | - | PRIMARY KEY | 记录唯一标识 |
| user_id | INTEGER | - | FOREIGN KEY | 关联用户 ID |
| crop_id | INTEGER | - | FOREIGN KEY | 关联作物 ID |
| image_url | VARCHAR | 255 | NOT NULL | 原始诊断图片存储路径 |
| disease_name | VARCHAR | 100 | - | AI 诊断病害名称 |
| advice | TEXT | - | - | 结构化防治建议内容 |
| confidence | FLOAT | - | - | 识别置信度数值 |
| duration | INTEGER | - | - | 接口响应耗时（毫秒） |
| create_time | DATETIME | - | SERVER_DEFAULT | 识别发起精确时间 |

### 7.5 问答消息表 (tb_message)

利用会话标识实现对话逻辑聚类，支撑用户与 AI 之间的多轮文本交互。

| **字段名** | **类型** | **长度** | **约束** | **描述** |
|---|---|---|---|---|
| id | INTEGER | - | PRIMARY KEY | 消息记录唯一 ID |
| user_id | INTEGER | - | FOREIGN KEY | 关联用户 ID |
| session_id | VARCHAR | 64 | NOT NULL, INDEX | 逻辑会话标识 |
| role | VARCHAR | 20 | NOT NULL | 发送者角色（user / ai） |
| content | TEXT | - | NOT NULL | 对话文本内容 |
| create_time | DATETIME | - | SERVER_DEFAULT | 消息发送精确时间 |