# 慧农 API 精简表

> 所有接口遵循统一响应格式 `{ code, message, data }`，以下仅列出 `data` 字段内容。
> 分页参数：`skip`（默认0）、`limit`（默认10，最大100）。
> 管理员接口需 `role=admin`，否则返回 `40301`。

## 用户模块

### 用户注册
- **方法**：`POST /users/register`
- **认证**：否
- **请求**：`{ username(str,3-50), password(str,8-20), phone(str,11)? }`
- **响应**：`{ id, username, phone, elder_mode, create_time }`

### 用户登录
- **方法**：`POST /users/login`
- **认证**：否
- **请求**：`{ username, password }`
- **响应**：`{ access_token: string, token_type: "bearer", user: { id, username, phone, elder_mode, create_time, role } }`
- **备注**：前端需存储 `access_token`，后续请求在 `Authorization: Bearer <token>` 头中携带。token 有效期 2 小时。

### 获取个人信息
- **方法**：`GET /users/me`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：无
- **响应**：`{ id, username, phone, elder_mode, create_time, role }`

### 更新个人信息
- **方法**：`PUT /users/me`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：`{ phone?, elder_mode? }`
- **响应**：更新后的用户对象

### 修改密码
- **方法**：`PUT /users/password`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：`{ old_password, new_password }`
- **响应**：`null`

---

## 资讯模块（普通用户）

### 资讯列表
- **方法**：`GET /news`
- **认证**：否
- **请求**：`?skip=0&limit=10&category=可选`
- **响应**：`{ total, list:[{ id, title, cover_url, publish_time, view_count }] }`

### 资讯详情
- **方法**：`GET /news/{id}`
- **认证**：否
- **请求**：路径 `id`
- **响应**：完整资讯对象（含 `content`）

---

## 资讯模块（管理员）

### 添加资讯
- **方法**：`POST /news`
- **认证**：是 (admin，需携带` Authorization: Bearer <token>`）
- **请求**：`{ title, content, category, cover_url? }`
- **响应**：新建资讯对象

### 编辑资讯
- **方法**：`PUT /news/{id}`
- **认证**：是 (admin，需携带` Authorization: Bearer <token>`）
- **请求**：路径 `id`, `{ title?, content?, category?, cover_url? }`
- **响应**：更新后的资讯对象

### 删除资讯
- **方法**：`DELETE /news/{id}`
- **认证**：是 (admin，需携带` Authorization: Bearer <token>`）
- **请求**：路径 `id`
- **响应**：`null`

---

## 病害识别模块

### 上传图片识别
- **方法**：`POST /crops/identify`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：`multipart/form-data`，字段 `file`，可选 `crop_name`（前端可传，若不传则后端从识别结果中提取）
- **响应**：`{ id, disease_name, crop_name, confidence, advice, image_url, create_time }`

### 识别历史列表
- **方法**：`GET /crops/history`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：`?skip=0&limit=10`
- **响应**：`{ total, list:[{ id, disease_name, crop_name, confidence, advice, image_url, create_time }] }`

### 识别记录详情
- **方法**：`GET /crops/history/{id}`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：路径 `id`
- **响应**：`{ id, user_id, image_url, disease_name, crop_name, confidence, advice, duration, create_time }`

### 删除识别记录
- **方法**：`DELETE /crops/history/{id}`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：路径 `id`
- **响应**：`null`

---

## 问诊模块

### WebSocket 流式对话
- **地址**：`ws://<host>/ws/chat?token=<access_token>`
- **认证**：是（token 作为查询参数）
- **发送**：`{ "content": "问题", "session_id": "可选" }`
- **接收**：流式 `{ "role":"ai", "content":"逐字", "is_end":false }`，结束时 `is_end:true`；连接成功返回 `{ "type":"connected", "session_id":"xxx" }`

### 获取会话列表
- **方法**：`GET /chat/sessions`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：`?skip=0&limit=20`
- **响应**：`{ total, list:[{ session_id, title, last_message_time }] }`

### 获取会话消息
- **方法**：`GET /chat/sessions/{session_id}/messages`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：`?skip=0&limit=20`
- **响应**：`{ total, list:[{ id, role, content, create_time }] }`

### 删除会话
- **方法**：`DELETE /chat/sessions/{session_id}`
- **认证**：是（需携带` Authorization: Bearer <token>`）
- **请求**：路径 `session_id`
- **响应**：`null`

---

## 后台管理（管理员专用）

### 用户列表
- **方法**：`GET /admin/users`
- **认证**：是 (admin，需携带` Authorization: Bearer <token>`）
- **请求**：`?skip=0&limit=20&keyword=可选`
- **响应**：`{ total, list:[{ id, username, phone, elder_mode, create_time }] }`