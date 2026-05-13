# 慧农 API 精简表

> 所有接口遵循统一响应格式 `{ code, message, data }`，以下仅列出 `data` 字段内容。
> 分页参数：`skip`（默认0）、`limit`（默认10，最大100）。
> **时间格式**：所有时间字段统一使用 ISO 8601 UTC，示例 `2026-04-16T10:00:00Z`。
> **图片 URL**：后端返回相对路径（如 `/uploads/xxx.jpg`），前端需根据运行环境拼接 `http://<host>:<port>` 前缀。

## 错误码表

| code  | 说明              | HTTP 状态码 |
| ----- | --------------- | -------- |
| 200   | 成功              | 200      |
| 40001 | 参数校验失败          | 400      |
| 40101 | 未授权（Token无效/过期） | 401      |
| 40301 | 无权限访问           | 403      |
| 40401 | 资源不存在（通用）       | 404      |
| 40402 | 用户不存在           | 404      |
| 40403 | 资讯不存在           | 404      |
| 40404 | 识别记录不存在         | 404      |
| 40901 | 用户名已存在          | 409      |
| 50000 | 服务器内部错误         | 500      |
| 50002 | 文件上传失败          | 500      |
| 50003 | AI 识别服务异常       | 500      |

---

## 用户模块

### 用户注册
- **方法**：`POST /users/register`
- **认证**：否
- **请求**：`{ username(str,3-50,字母数字下划线), password(str,8-20,需含字母+数字), phone(str,11)? }`
- **响应**：`{ id, username, phone, elder_mode, role, create_time }`
- **错误**：用户名已存在 → `409` / `code: 40901`

### 用户登录
- **方法**：`POST /users/login`
- **认证**：否
- **请求**：`{ username, password }`
- **响应**：`{ access_token, token_type: "bearer", user: { id, username, phone, elder_mode, create_time, role } }`
- **备注**：前端存储 `access_token`，后续请求在 `Authorization: Bearer <token>` 头中携带。token 有效期 2 小时。

### 获取个人信息
- **方法**：`GET /users/me`
- **认证**：是
- **响应**：`{ id, username, phone, elder_mode, create_time, role }`

### 更新个人信息
- **方法**：`PUT /users/me`
- **认证**：是
- **请求**：`{ phone?, elder_mode? }`（可选，只传需要修改的项）
- **响应**：更新后的用户对象

### 修改密码
- **方法**：`PUT /users/password`
- **认证**：是
- **请求**：`{ old_password, new_password(str,8-20,需含字母+数字) }`
- **响应**：`null`
- **错误**：旧密码错误 → `400` / `code: 40001`

---

## 资讯模块（普通用户）

### 资讯列表
- **方法**：`GET /news`
- **认证**：否
- **请求**：`?skip=0&limit=10`
- **响应**：`{ total, list:[{ id, title, content, category, cover_url, publish_time, view_count }] }`
- **备注**：列表包含正文内容概要，完整正文请调用详情接口

### 资讯详情
- **方法**：`GET /news/{id}`
- **认证**：否
- **请求**：路径 `id`
- **响应**：`{ id, title, content, category, cover_url, publish_time, view_count }`

---

## 资讯模块（管理员）

### 添加资讯
- **方法**：`POST /news`
- **认证**：是 (admin)
- **请求**：`{ title, content, category("政策"/"农技"/"市场"/"预警"), cover_url? }`
- **响应**：新建资讯对象（同上完整对象）
- **错误**：非管理员 → `403` / `code: 40301`

### 编辑资讯
- **方法**：`PUT /news/{id}`
- **认证**：是 (admin)
- **请求**：`{ title, content, category("政策"/"农技"/"市场"/"预警"), cover_url? }`（全字段更新）
- **响应**：更新后的资讯对象
- **错误**：资讯不存在 → `404` / `code: 40403`；非管理员 → `403` / `code: 40301`

### 删除资讯
- **方法**：`DELETE /news/{id}`
- **认证**：是 (admin)
- **请求**：路径 `id`
- **响应**：`null`
- **错误**：资讯不存在 → `404` / `code: 40403`；非管理员 → `403` / `code: 40301`

---

## 病害识别模块

### 上传图片识别
- **方法**：`POST /crops/identify`
- **认证**：是
- **请求**：`multipart/form-data`，必选字段 `file`（jpg/png，≤10MB），可选字段 `crop_name`
- **响应**：`{ id, image_url, crop_name, disease_name, advice, confidence, duration, create_time }`
- **错误**：上传失败 → `500` / `code: 50002`；AI 服务异常 → `500` / `code: 50003`

### 识别历史列表
- **方法**：`GET /crops/history`
- **认证**：是
- **请求**：`?skip=0&limit=10`
- **响应**：`{ total, list:[{ id, image_url, crop_name, disease_name, confidence, create_time }] }`
- **备注**：如需查看防治建议（`advice`），调用识别记录详情接口

### 识别记录详情
- **方法**：`GET /crops/history/{id}`
- **认证**：是
- **请求**：路径 `id`
- **响应**：`{ id, image_url, crop_name, disease_name, advice, confidence, duration, create_time }`
- **错误**：记录不存在 → `404` / `code: 40404`

### 删除识别记录
- **方法**：`DELETE /crops/history/{id}`
- **认证**：是
- **请求**：路径 `id`
- **响应**：`null`
- **错误**：记录不存在 → `404` / `code: 40404`

---

## 问诊模块

### 文本对话
- **方法**：`POST /chat/message`
- **认证**：是
- **请求**：`multipart/form-data`，必选字段 `content`，可选字段 `session_id`
- **响应**：`{ answer: string, session_id: string }`
- **备注**：不传 `session_id` 时自动创建新会话，标题取第一条用户消息的前20字符

### 图片对话
- **方法**：`POST /chat/message_with_image`
- **认证**：是
- **请求**：`multipart/form-data`，必选字段 `file`（jpg/png，≤10MB），可选字段 `content`、`session_id`
- **响应**：`{ answer: string, session_id: string, image_url: string }`
- **备注**：`content` 可选。若不传，后端自动使用默认提示词 `"请分析上传的图片"`。图片会上传到本地并持久化到消息记录

### 获取会话列表
- **方法**：`GET /chat/sessions`
- **认证**：是
- **请求**：`?skip=0&limit=20`
- **响应**：`{ total, list:[{ session_id, title, last_message_time }] }`
- **备注**：`title` 由后端自动取该会话第一条用户消息的前20字符生成

### 获取会话消息
- **方法**：`GET /chat/sessions/{session_id}/messages`
- **认证**：是
- **请求**：`?skip=0&limit=20`
- **响应**：`{ total, list:[{ id, role, content, image_url?, create_time }] }`
- **备注**：`image_url` 仅图片消息有值，纯文本消息为 `null`
- **错误**：会话不存在 → `404` / `code: 40401`

### 删除会话
- **方法**：`DELETE /chat/sessions/{session_id}`
- **认证**：是
- **请求**：路径 `session_id`
- **响应**：`null`
- **错误**：会话不存在 → `404` / `code: 40401`
- **备注**：删除会话会同步删除其下所有消息
