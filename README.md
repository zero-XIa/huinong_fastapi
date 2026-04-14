# 慧农平台后端接口文档 (v1.0.0)

**文档版本**: v1.0.0  
**最后更新**: 2026-04-12  
**Base URL**: `http://<server-ip>:8000/api/v1`

---

## 目录

1. [全局约定](#1-全局约定)
2. [错误码总表](#2-错误码总表)
3. [数据模型 (Schema)](#3-数据模型-schema)
4. [用户管理模块](#4-用户管理模块)
5. [作物识别模块](#5-作物识别模块)
6. [农业资讯模块](#6-农业资讯模块)
7. [智能问答模块](#7-智能问答模块)
8. [变更记录](#8-变更记录)

---

## 1. 全局约定

### 1.1 基础信息

- **Base URL**: `http://<server-ip>:8000/api/v1`
- **认证方式**: JWT Token，放在请求头 `Authorization: Bearer <token>`
- **请求格式**: 
  - JSON 数据：`Content-Type: application/json`
  - 文件上传：`Content-Type: multipart/form-data`
- **响应格式**: `Content-Type: application/json`

### 1.2 统一响应格式

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

#### 错误响应

```json
{
  "code": 40001,
  "message": "参数校验失败",
  "data": null
}
```

### 1.3 认证说明

- **不需要认证的接口**: 
  - `POST /users/register` (用户注册)
  - `POST /users/login` (用户登录)
  - `GET /` (欢迎接口)
- **其他所有接口均需要 JWT Token 认证**
- Token 有效期：2 小时
- Token 刷新：通过重新登录获取新 Token

### 1.4 通用校验规则

- **用户名**: 长度 3-50，只允许字母、数字、下划线
- **密码**: 长度 8-20，必须包含字母和数字
- **手机号**: 可选，如果提供则必须是 11 位数字，以 1 开头
- **分页参数**: 
  - `skip`: 整数，>= 0，默认 0
  - `limit`: 整数，1-100，默认 10

---

## 2. 错误码总表

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 200 | 成功 | 200 |
| 40001 | 参数校验失败 | 200 |
| 40002 | 请求格式错误 | 200 |
| 40101 | 未授权（Token 无效或过期） | 200 |
| 40102 | 未登录 | 200 |
| 40301 | 无权限访问 | 200 |
| 40401 | 资源不存在 | 200 |
| 40402 | 用户不存在 | 200 |
| 40403 | 资讯不存在 | 200 |
| 40404 | 识别记录不存在 | 200 |
| 40901 | 资源冲突（用户名已存在） | 200 |
| 40902 | 手机号已绑定 | 200 |
| 50000 | 服务器内部错误 | 200 |
| 50001 | 数据库错误 | 200 |
| 50002 | 文件上传失败 | 200 |
| 50003 | AI 识别服务异常 | 200 |

---

## 3. 数据模型 (Schema)

### 3.1 User (用户对象)

```json
{
  "id": 1,
  "username": "user123",
  "phone": "13800138000",
  "elder_mode": false,
  "create_time": "2026-03-16T12:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 用户唯一自增 ID |
| username | string | 登录账号 |
| phone | string | 用户绑定手机号（可选） |
| elder_mode | boolean | 长辈模式开关状态 |
| create_time | string (datetime) | 账号注册时间（ISO 8601 格式） |

### 3.2 News (资讯对象)

```json
{
  "id": 1,
  "title": "2026 年春耕补贴",
  "content": "这里是详细的正文内容...",
  "category": "政策",
  "cover_url": "http://example.com/image.jpg",
  "publish_time": "2026-03-14T10:00:00Z",
  "view_count": 15
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 资讯唯一 ID |
| title | string | 资讯标题（1-200 字符） |
| content | string | 资讯正文（支持 Markdown/HTML） |
| category | string | 分类（政策/预警/农技/市场等） |
| cover_url | string | 封面图地址（可选） |
| publish_time | string (datetime) | 发布时间（ISO 8601 格式） |
| view_count | integer | 阅读量 |

### 3.3 Identification (识别记录对象)

```json
{
  "id": 1,
  "user_id": 1,
  "crop_id": 1,
  "crop_name": "水稻",
  "image_url": "http://example.com/images/123.jpg",
  "disease_name": "水稻稻瘟病",
  "advice": "建议喷施三环唑，并加强田间水分管理...",
  "confidence": 0.98,
  "duration": 1250,
  "create_time": "2026-03-16T14:30:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 记录唯一标识 |
| user_id | integer | 关联用户 ID |
| crop_id | integer | 关联作物 ID |
| crop_name | string | 作物名称 |
| image_url | string | 原始诊断图片存储路径 |
| disease_name | string | AI 诊断病害名称 |
| advice | string | 结构化防治建议内容 |
| confidence | float | 识别置信度（0-1） |
| duration | integer | 接口响应耗时（毫秒） |
| create_time | string (datetime) | 识别发起精确时间 |

### 3.4 ChatMessage (聊天消息对象)

```json
{
  "id": 1,
  "user_id": 1,
  "session_id": "abc123def456",
  "role": "user",
  "content": "水稻叶子发黄怎么办？",
  "create_time": "2026-03-16T15:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 消息记录唯一 ID |
| user_id | integer | 关联用户 ID |
| session_id | string | 逻辑会话标识（64 字符） |
| role | string | 发送者角色（user/ai） |
| content | string | 对话文本内容 |
| create_time | string (datetime) | 消息发送精确时间 |

---

## 4. 用户管理模块

### 4.1 用户注册

- **接口名称**: 用户注册
- **URL**: `POST /users/register`
- **认证**: 不需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| username | string | 是 | 长度 3-50，只允许字母、数字、下划线 | 登录账号 |
| password | string | 是 | 长度 8-20，必须包含字母和数字 | 登录密码 |
| phone | string | 否 | 11 位数字，以 1 开头 | 手机号 |

#### 请求示例

```json
{
  "username": "user123",
  "password": "password123",
  "phone": "13800138000"
}
```

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "user123",
    "phone": "13800138000",
    "elder_mode": false,
    "create_time": "2026-03-16T12:00:00Z"
  }
}
```

#### 失败响应

**用户名已存在**

```json
{
  "code": 40901,
  "message": "用户名已存在",
  "data": null
}
```

**手机号已绑定**

```json
{
  "code": 40902,
  "message": "手机号已绑定其他账号",
  "data": null
}
```

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：密码必须包含字母和数字",
  "data": null
}
```

---

### 4.2 用户登录

- **接口名称**: 用户登录
- **URL**: `POST /users/login`
- **认证**: 不需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| username | string | 是 | 长度 3-50 | 登录账号 |
| password | string | 是 | 长度 8-20 | 登录密码 |

#### 请求示例

```json
{
  "username": "user123",
  "password": "password123"
}
```

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "user123",
      "phone": "13800138000",
      "elder_mode": false,
      "create_time": "2026-03-16T12:00:00Z"
    }
  }
}
```

#### 失败响应

**用户名或密码错误**

```json
{
  "code": 40101,
  "message": "用户名或密码错误",
  "data": null
}
```

**用户不存在**

```json
{
  "code": 40402,
  "message": "用户不存在",
  "data": null
}
```

---

### 4.3 获取用户信息

- **接口名称**: 获取用户信息
- **URL**: `GET /users/me`
- **认证**: 需要

#### 请求参数

无

#### 请求示例

无（GET 请求）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "user123",
    "phone": "13800138000",
    "elder_mode": false,
    "create_time": "2026-03-16T12:00:00Z"
  }
}
```

#### 失败响应

**未授权**

```json
{
  "code": 40101,
  "message": "Token 无效或已过期",
  "data": null
}
```

---

### 4.4 更新用户信息

- **接口名称**: 更新用户信息
- **URL**: `PUT /users/me`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| phone | string | 否 | 11 位数字，以 1 开头 | 手机号 |
| elder_mode | boolean | 否 | - | 长辈模式 |

#### 请求示例

```json
{
  "phone": "13900139000",
  "elder_mode": true
}
```

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "user123",
    "phone": "13900139000",
    "elder_mode": true,
    "create_time": "2026-03-16T12:00:00Z"
  }
}
```

#### 失败响应

**手机号已绑定**

```json
{
  "code": 40902,
  "message": "手机号已绑定其他账号",
  "data": null
}
```

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：手机号格式不正确",
  "data": null
}
```

---

### 4.5 修改密码

- **接口名称**: 修改密码
- **URL**: `PUT /users/password`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| old_password | string | 是 | 长度 8-20 | 原密码 |
| new_password | string | 是 | 长度 8-20，必须包含字母和数字 | 新密码 |

#### 请求示例

```json
{
  "old_password": "password123",
  "new_password": "newpassword456"
}
```

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

#### 失败响应

**原密码错误**

```json
{
  "code": 40101,
  "message": "原密码错误",
  "data": null
}
```

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：新密码必须包含字母和数字",
  "data": null
}
```

---

## 5. 作物识别模块

### 5.1 上传并识别病害

- **接口名称**: 上传并识别病害
- **URL**: `POST /crops/identify`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| file | file | 是 | 图片格式（jpg/jpeg/png），最大 10MB | 作物图片 |
| crop_id | integer | 否 | 正整数 | 作物类型 ID（可选，用于提高识别精度） |

#### 请求示例

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="crop.jpg"
Content-Type: image/jpeg

<binary data>
------WebKitFormBoundary
Content-Disposition: form-data; name="crop_id"

1
------WebKitFormBoundary--
```

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "crop_id": 1,
    "crop_name": "水稻",
    "image_url": "http://example.com/images/123.jpg",
    "disease_name": "水稻稻瘟病",
    "advice": "建议喷施三环唑，并加强田间水分管理，避免氮肥过量。",
    "confidence": 0.98,
    "duration": 1250,
    "create_time": "2026-03-16T14:30:00Z"
  }
}
```

#### 失败响应

**文件上传失败**

```json
{
  "code": 50002,
  "message": "文件上传失败：文件格式不支持",
  "data": null
}
```

**AI 识别服务异常**

```json
{
  "code": 50003,
  "message": "AI 识别服务暂时不可用，请稍后重试",
  "data": null
}
```

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：图片大小不能超过 10MB",
  "data": null
}
```

---

### 5.2 获取识别历史记录

- **接口名称**: 获取识别历史记录
- **URL**: `GET /crops/history`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| skip | integer | 否 | >= 0，默认 0 | 跳过的记录数 |
| limit | integer | 否 | 1-100，默认 10 | 每页获取条数 |

#### 请求示例

无（GET 请求）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 25,
    "list": [
      {
        "id": 1,
        "crop_id": 1,
        "crop_name": "水稻",
        "image_url": "http://example.com/images/123.jpg",
        "disease_name": "水稻稻瘟病",
        "advice": "建议...",
        "confidence": 0.98,
        "duration": 1250,
        "create_time": "2026-03-16T14:30:00Z"
      },
      {
        "id": 2,
        "crop_id": 2,
        "crop_name": "小麦",
        "image_url": "http://example.com/images/124.jpg",
        "disease_name": "小麦白粉病",
        "advice": "建议...",
        "confidence": 0.95,
        "duration": 1180,
        "create_time": "2026-03-15T10:20:00Z"
      }
    ]
  }
}
```

#### 失败响应

**未授权**

```json
{
  "code": 40101,
  "message": "Token 无效或已过期",
  "data": null
}
```

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：limit 必须在 1-100 之间",
  "data": null
}
```

---

### 5.3 获取识别记录详情

- **接口名称**: 获取识别记录详情
- **URL**: `GET /crops/history/{id}`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| id | integer | 是 | 正整数 | 识别记录 ID |

#### 请求示例

无（路径参数）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "crop_id": 1,
    "crop_name": "水稻",
    "image_url": "http://example.com/images/123.jpg",
    "disease_name": "水稻稻瘟病",
    "advice": "建议喷施三环唑，并加强田间水分管理，避免氮肥过量。",
    "confidence": 0.98,
    "duration": 1250,
    "create_time": "2026-03-16T14:30:00Z"
  }
}
```

#### 失败响应

**记录不存在**

```json
{
  "code": 40404,
  "message": "识别记录不存在",
  "data": null
}
```

**无权限访问**

```json
{
  "code": 40301,
  "message": "无权限访问该记录",
  "data": null
}
```

---

### 5.4 删除识别记录

- **接口名称**: 删除识别记录
- **URL**: `DELETE /crops/history/{id}`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| id | integer | 是 | 正整数 | 识别记录 ID |

#### 请求示例

无（路径参数）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

#### 失败响应

**记录不存在**

```json
{
  "code": 40404,
  "message": "识别记录不存在",
  "data": null
}
```

**无权限访问**

```json
{
  "code": 40301,
  "message": "无权限删除该记录",
  "data": null
}
```

---

## 6. 农业资讯模块

### 6.1 分页获取资讯列表

- **接口名称**: 分页获取资讯列表
- **URL**: `GET /news`
- **认证**: 不需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| skip | integer | 否 | >= 0，默认 0 | 跳过的记录数 |
| limit | integer | 否 | 1-100，默认 10 | 每页获取条数 |
| category | string | 否 | - | 分类筛选（政策/预警/农技/市场） |

#### 请求示例

无（GET 请求）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "list": [
      {
        "id": 1,
        "title": "2026 年春耕补贴",
        "content": "资讯内容摘要...",
        "category": "政策",
        "cover_url": "http://example.com/image1.jpg",
        "publish_time": "2026-03-14T10:00:00Z",
        "view_count": 15
      },
      {
        "id": 2,
        "title": "小麦病虫害防治技术",
        "content": "资讯内容摘要...",
        "category": "农技",
        "cover_url": "http://example.com/image2.jpg",
        "publish_time": "2026-03-13T09:00:00Z",
        "view_count": 28
      }
    ]
  }
}
```

#### 失败响应

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：limit 必须在 1-100 之间",
  "data": null
}
```

---

### 6.2 获取资讯详情

- **接口名称**: 获取资讯详情
- **URL**: `GET /news/{id}`
- **认证**: 不需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| id | integer | 是 | 正整数 | 资讯 ID |

#### 请求示例

无（路径参数）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "2026 年春耕补贴",
    "content": "这里是详细的 Markdown 或 HTML 正文内容...",
    "category": "政策",
    "cover_url": "http://example.com/image1.jpg",
    "publish_time": "2026-03-14T10:00:00Z",
    "view_count": 16
  }
}
```

#### 失败响应

**资讯不存在**

```json
{
  "code": 40403,
  "message": "资讯不存在",
  "data": null
}
```

---

### 6.3 添加资讯

- **接口名称**: 添加资讯
- **URL**: `POST /news`
- **认证**: 需要（管理员权限）

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| title | string | 是 | 长度 1-200 | 资讯标题 |
| content | string | 是 | 长度 1-50000 | 资讯正文 |
| category | string | 是 | 枚举值：政策/预警/农技/市场 | 资讯分类 |
| cover_url | string | 否 | 有效 URL 格式 | 封面图地址 |

#### 请求示例

```json
{
  "title": "新的资讯标题",
  "content": "新的资讯详细内容...",
  "category": "技术",
  "cover_url": "http://example.com/image.jpg"
}
```

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 2,
    "title": "新的资讯标题",
    "content": "新的资讯详细内容...",
    "category": "技术",
    "cover_url": "http://example.com/image.jpg",
    "publish_time": "2026-03-16T14:00:00Z",
    "view_count": 0
  }
}
```

#### 失败响应

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：标题长度不能超过 200 字符",
  "data": null
}
```

**无权限访问**

```json
{
  "code": 40301,
  "message": "无权限执行此操作",
  "data": null
}
```

---

### 6.4 更新资讯

- **接口名称**: 更新资讯
- **URL**: `PUT /news/{id}`
- **认证**: 需要（管理员权限）

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| title | string | 否 | 长度 1-200 | 资讯标题 |
| content | string | 否 | 长度 1-50000 | 资讯正文 |
| category | string | 否 | 枚举值：政策/预警/农技/市场 | 资讯分类 |
| cover_url | string | 否 | 有效 URL 格式 | 封面图地址 |

#### 请求示例

```json
{
  "title": "更新后的资讯标题",
  "content": "更新后的资讯详细内容...",
  "category": "政策"
}
```

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "更新后的资讯标题",
    "content": "更新后的资讯详细内容...",
    "category": "政策",
    "cover_url": "http://example.com/image1.jpg",
    "publish_time": "2026-03-14T10:00:00Z",
    "view_count": 16
  }
}
```

#### 失败响应

**资讯不存在**

```json
{
  "code": 40403,
  "message": "资讯不存在",
  "data": null
}
```

**参数校验失败**

```json
{
  "code": 40001,
  "message": "参数校验失败：分类必须是政策、预警、农技或市场",
  "data": null
}
```

---

### 6.5 删除资讯

- **接口名称**: 删除资讯
- **URL**: `DELETE /news/{id}`
- **认证**: 需要（管理员权限）

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| id | integer | 是 | 正整数 | 资讯 ID |

#### 请求示例

无（路径参数）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

#### 失败响应

**资讯不存在**

```json
{
  "code": 40403,
  "message": "资讯不存在",
  "data": null
}
```

**无权限访问**

```json
{
  "code": 40301,
  "message": "无权限删除该资讯",
  "data": null
}
```

---

## 7. 智能问答模块

### 7.1 实时对话流 (WebSocket)

- **接口名称**: 实时对话流
- **URL**: `WS /ws/chat`
- **认证**: 需要（通过 Query 参数传递 token）

#### 连接方式

```
ws://<server-ip>:8000/ws/chat?token=<jwt_token>
```

#### 发送报文格式

```json
{
  "content": "水稻叶子发黄怎么办？",
  "session_id": "abc123def456"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 用户问题内容 |
| session_id | string | 否 | 会话 ID（不提供则自动生成新会话） |

#### 接收报文格式

**流式返回（逐字）**

```json
{
  "role": "ai",
  "content": "水",
  "is_end": false
}
```

**结束标识**

```json
{
  "role": "ai",
  "content": "",
  "is_end": true
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| role | string | 角色（ai） |
| content | string | AI 回复内容（逐字返回） |
| is_end | boolean | 是否结束（true 表示回复完成） |

#### 连接成功示例

```json
{
  "type": "connected",
  "session_id": "abc123def456",
  "message": "连接成功"
}
```

#### 错误响应

**Token 无效**

```json
{
  "type": "error",
  "code": 40101,
  "message": "Token 无效或已过期"
}
```

**服务器错误**

```json
{
  "type": "error",
  "code": 50000,
  "message": "服务器内部错误"
}
```

---

### 7.2 获取历史对话记录

- **接口名称**: 获取历史对话记录
- **URL**: `GET /chat/history`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| session_id | string | 否 | 64 字符 | 会话 ID（不提供则返回所有会话列表） |
| skip | integer | 否 | >= 0，默认 0 | 跳过的记录数 |
| limit | integer | 否 | 1-100，默认 20 | 每页获取条数 |

#### 请求示例

无（GET 请求）

#### 成功响应（获取会话列表）

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "sessions": [
      {
        "session_id": "abc123def456",
        "last_message_time": "2026-03-16T15:30:00Z",
        "message_count": 10
      },
      {
        "session_id": "xyz789uvw012",
        "last_message_time": "2026-03-15T14:20:00Z",
        "message_count": 5
      }
    ]
  }
}
```

#### 成功响应（获取会话详情）

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "abc123def456",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "水稻叶子发黄怎么办？",
        "create_time": "2026-03-16T15:00:00Z"
      },
      {
        "id": 2,
        "role": "ai",
        "content": "水稻叶子发黄可能是由于...",
        "create_time": "2026-03-16T15:00:05Z"
      }
    ],
    "total": 10
  }
}
```

#### 失败响应

**未授权**

```json
{
  "code": 40101,
  "message": "Token 无效或已过期",
  "data": null
}
```

**会话不存在**

```json
{
  "code": 40401,
  "message": "会话不存在",
  "data": null
}
```

---

### 7.3 删除会话

- **接口名称**: 删除会话
- **URL**: `DELETE /chat/session/{session_id}`
- **认证**: 需要

#### 请求参数

| 参数名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|----------|------|
| session_id | string | 是 | 64 字符 | 会话 ID |

#### 请求示例

无（路径参数）

#### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

#### 失败响应

**会话不存在**

```json
{
  "code": 40401,
  "message": "会话不存在",
  "data": null
}
```

**无权限访问**

```json
{
  "code": 40301,
  "message": "无权限删除该会话",
  "data": null
}
```

---

## 8. 变更记录

| 版本号 | 日期 | 修改内容 | 修改人 |
|--------|------|----------|--------|
| v1.0.0 | 2026-04-12 | 初始版本，包含完整的接口契约文档 | - |

### v1.0.0 主要更新内容

1. **全局约定规范化**
   - 统一 Base URL 为 `/api/v1`
   - 新增 JWT Token 认证机制
   - 统一成功/错误响应格式
   - 补充通用校验规则

2. **错误码体系**
   - 新增完整的错误码总表
   - 区分业务错误码和 HTTP 状态码

3. **数据模型**
   - 新增 User、News、Identification、ChatMessage 数据模型定义
   - 明确各字段类型和说明

4. **用户管理模块**
   - 新增获取用户信息接口
   - 新增更新用户信息接口
   - 新增修改密码接口
   - 完善登录接口返回（包含 token）

5. **作物识别模块**
   - 新增获取识别记录详情接口
   - 新增删除识别记录接口
   - 完善文件上传校验规则

6. **农业资讯模块**
   - 新增更新资讯接口
   - 新增删除资讯接口
   - 完善分页参数校验

7. **智能问答模块**
   - 新增历史对话记录接口
   - 新增删除会话接口
   - 完善 WebSocket 连接认证方式

---

## 附录

### A. 常见场景示例

#### A.1 完整的新用户流程

1. 用户注册
2. 用户登录获取 token
3. 使用 token 访问需要认证的接口

#### A.2 作物识别流程

1. 登录获取 token
2. 上传作物图片进行识别
3. 查看识别历史记录
4. 查看识别记录详情

#### A.3 WebSocket 聊天流程

1. 登录获取 token
2. 使用 token 建立 WebSocket 连接
3. 发送问题并接收流式回复
4. 保存会话 ID
5. 后续可通过会话 ID 查看历史对话

### B. 最佳实践

1. **Token 管理**: 建议客户端在本地缓存 token，并在 40101 错误时自动刷新 token 或跳转登录
2. **分页处理**: 建议使用 skip 和 limit 进行分页，避免一次性加载大量数据
3. **错误处理**: 建议客户端根据 code 而非 HTTP 状态码进行业务错误处理
4. **WebSocket 重连**: 建议实现自动重连机制，在网络不稳定时保持连接
