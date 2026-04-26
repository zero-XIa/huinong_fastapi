# Dify 工作流编排对话型应用 API 参考

## 基础 URL

```
https://api.dify.ai/v1
```

## 鉴权

Service API 使用 `API-Key` 进行鉴权。
**强烈建议开发者把 `API-Key` 放在后端存储，而非分享或者放在客户端存储，以免 `API-Key` 泄露，导致财产损失。**
所有 API 请求都应在 **`Authorization`** HTTP Header 中包含您的 `API-Key`，如下所示：

```
Authorization: Bearer {API_KEY}
```

---

## 发送对话消息

**POST** `/chat-messages`

创建会话消息。

### Request Body

| 参数 | 类型 | 描述 |
|------|------|------|
| `query` | string | 用户输入/提问内容。 |
| `inputs` | object | 允许传入 App 定义的各变量值。inputs 参数包含了多组键值对（Key/Value pairs），每组的键对应一个特定变量，每组的值则是该变量的具体值。如果变量是文件类型，请指定一个包含以下 `files` 中所述键的对象。默认 `{}` |
| `response_mode` | string | `streaming` 流式模式（推荐）。基于 SSE（Server-Sent Events）实现类似打字机输出方式的流式返回。<br>`blocking` 阻塞模式，等待执行完毕后返回结果。（请求若流程较长可能会被中断）。由于 Cloudflare 限制，请求会在 100 秒超时无返回后中断。 |
| `user` | string | 用户标识，用于定义终端用户的身份，方便检索、统计。由开发者定义规则，需保证用户标识在应用内唯一。服务 API 不会共享 WebApp 创建的对话。 |
| `conversation_id` | string | （选填）会话 ID，需要基于之前的聊天记录继续对话，必须传之前消息的 conversation_id。 |
| `files` | array[object] | 文件列表，适用于传入文件结合文本理解并回答问题，仅当模型支持 Vision/Video 能力时可用。<br>- `type` (string) 支持类型：`document`（TXT, MD, MARKDOWN, MDX, PDF, HTML, XLSX, XLS, VTT, PROPERTIES, DOC, DOCX, CSV, EML, MSG, PPTX, PPT, XML, EPUB）、`image`（JPG, JPEG, PNG, GIF, WEBP, SVG）、`audio`（MP3, M4A, WAV, WEBM, MPGA）、`video`（MP4, MOV, MPEG, WEBM）、`custom`（其他文件类型）<br>- `transfer_method` (string) 传递方式：`remote_url`（文件地址）或 `local_file`（上传文件）<br>- `url` 文件地址（仅当 transfer_method 为 `remote_url` 时）<br>- `upload_file_id` 上传文件 ID（仅当 transfer_method 为 `local_file` 时） |
| `auto_generate_name` | bool | （选填）自动生成标题，默认 `true`。若设置为 `false`，则可通过调用会话重命名接口并设置 `auto_generate` 为 `true` 实现异步生成标题。 |
| `workflow_id` | string | （选填）工作流 ID，用于指定特定版本，如果不提供则使用默认的已发布版本。 |
| `trace_id` | string | （选填）链路追踪 ID。适用于与业务系统已有的 trace 组件打通，实现端到端分布式追踪等场景。如果未指定，系统会自动生成 `trace_id`。支持以下三种方式传递，优先级依次为：<br>- Header：通过 HTTP Header `X-Trace-Id` 传递<br>- Query 参数：通过 URL 查询参数 `trace_id` 传递<br>- Request Body：通过请求体字段 `trace_id` 传递（即本字段） |

### Response

当 `response_mode` 为 `blocking` 时，返回 ChatCompletionResponse object。
当 `response_mode` 为 `streaming` 时，返回 ChunkChatCompletionResponse object 流式序列。

#### ChatCompletionResponse

返回完整的 App 结果，`Content-Type` 为 `application/json`。

- `event` (string) 事件类型，固定为 `message`
- `task_id` (string) 任务 ID，用于请求跟踪和下方的停止响应接口
- `id` (string) 唯一 ID
- `message_id` (string) 消息唯一 ID
- `conversation_id` (string) 会话 ID
- `mode` (string) App 模式，固定为 chat
- `answer` (string) 完整回复内容
- `metadata` (object) 元数据
  - `usage` (Usage) 模型用量信息
  - `retriever_resources` (array[RetrieverResource]) 引用和归属分段列表
- `created_at` (int) 消息创建时间戳，如：1705395332

#### ChunkChatCompletionResponse

返回 App 输出的流式块，`Content-Type` 为 `text/event-stream`。
每个流式块均为 data: 开头，块之间以 \n\n 即两个换行符分隔，如下所示：

```
data: {"event": "message", "task_id": "900bbd43-dc0b-4383-a372-aa6e6c414227", "id": "663c5084-a254-4040-8ad3-51f2a3c1a77c", "answer": "Hi", "created_at": 1705398420}

```

流式块中根据 event 不同，结构也不同：

- **`event: message`** LLM 返回文本块事件
  - `task_id` (string) 任务 ID
  - `message_id` (string) 消息唯一 ID
  - `conversation_id` (string) 会话 ID
  - `answer` (string) LLM 返回文本块内容
  - `created_at` (int) 创建时间戳
- **`event: message_file`** 文件事件
  - `id` (string) 文件唯一 ID
  - `type` (string) 文件类型，目前仅为 image
  - `belongs_to` (string) 文件归属，user 或 assistant
  - `url` (string) 文件访问地址
  - `conversation_id` (string) 会话 ID
- **`event: message_end`** 消息结束事件
  - `task_id` (string) 任务 ID
  - `message_id` (string) 消息唯一 ID
  - `conversation_id` (string) 会话 ID
  - `metadata` (object) 元数据
- **`event: tts_message`** TTS 音频流事件
  - `task_id` (string) 任务 ID
  - `message_id` (string) 消息唯一 ID
  - `audio` (string) 音频块 Base64 编码文本
  - `created_at` (int) 创建时间戳
- **`event: tts_message_end`** TTS 音频流结束事件
- **`event: message_replace`** 消息内容替换事件
- **`event: workflow_started`** workflow 开始执行
- **`event: node_started`** node 开始执行
- **`event: node_finished`** node 执行结束
- **`event: workflow_finished`** workflow 执行结束
- **`event: error`** 流式输出过程中出现的异常
- **`event: ping`** 每 10s 一次的 ping 事件

### 请求示例（阻塞模式）

```bash
curl -X POST 'https://api.dify.ai/v1/chat-messages' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "inputs": {},
  "query": "What are the specs of the iPhone 13 Pro Max?",
  "response_mode": "blocking",
  "conversation_id": "",
  "user": "abc-123"
}'
```

阻塞模式响应示例：

```json
{
    "event": "message",
    "task_id": "c3800678-a077-43df-a102-53f23ed20b88",
    "id": "9da23599-e713-473b-982c-4328d4f5c78a",
    "message_id": "9da23599-e713-473b-982c-4328d4f5c78a",
    "conversation_id": "45701982-8118-4bc5-8e9b-64562b4555f2",
    "mode": "chat",
    "answer": "iPhone 13 Pro Max specs are listed here:...",
    "metadata": {
        "usage": { ... },
        "retriever_resources": [ ... ]
    },
    "created_at": 1705407629
}
```

### 请求示例（流式模式）

```bash
curl -X POST 'https://api.dify.ai/v1/chat-messages' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "inputs": {},
  "query": "What are the specs of the iPhone 13 Pro Max?",
  "response_mode": "streaming",
  "conversation_id": "",
  "user": "abc-123",
  "files": [
      {
          "type": "image",
          "transfer_method": "remote_url",
          "url": "https://cloud.dify.ai/logo/logo-site.png"
      }
  ]
}'
```

流式模式响应示例（片段）：

```
data: {"event": "workflow_started", "task_id": "5ad4cb98-f0c7-4085-b384-88c403be6290", ...}
data: {"event": "node_started", ...}
data: {"event": "node_finished", ...}
data: {"event": "workflow_finished", ...}
data: {"event": "message", "answer": " I", ...}
data: {"event": "message", "answer": "'m", ...}
data: {"event": "message_end", ...}
data: {"event": "tts_message", "audio": "...", ...}
data: {"event": "tts_message_end", ...}
```

---

## 上传文件

**POST** `/files/upload`

上传文件并在发送消息时使用，可实现图文多模态理解。支持您的应用程序所支持的所有格式。
*上传的文件仅供当前终端用户使用。*

### Request Body

该接口需使用 `multipart/form-data` 进行请求。

| 参数 | 类型 | 描述 |
|------|------|------|
| `file` | file | 要上传的文件。 |
| `user` | string | 用户标识，用于定义终端用户的身份，必须和发送消息接口传入 user 保持一致。 |

### 请求示例

```bash
curl -X POST 'https://api.dify.ai/v1/files/upload' \
--header 'Authorization: Bearer {api_key}' \
--form 'file=@localfile;type=image/[png|jpeg|jpg|webp|gif]' \
--form 'user=abc-123'
```

### 响应示例

```json
{
  "id": "72fa9618-8f89-4a37-9b33-7e1178a24a67",
  "name": "example.png",
  "size": 1024,
  "extension": "png",
  "mime_type": "image/png",
  "created_by": 123,
  "created_at": 1577836800
}
```

---

## 获取终端用户

**GET** `/end-users/:end_user_id`

通过终端用户 ID 获取终端用户信息。

### 路径参数

| 参数 | 描述 |
|------|------|
| `end_user_id` (uuid) | 终端用户 ID。 |

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/end-users/6ad1ab0a-73ff-4ac1-b9e4-cdb312f71f13' \
--header 'Authorization: Bearer {api_key}'
```

### 响应示例

```json
{
  "id": "6ad1ab0a-73ff-4ac1-b9e4-cdb312f71f13",
  "tenant_id": "8c0f3f3a-66b0-4b55-a0bf-8b8e0d6aee7d",
  "app_id": "6c8c3f41-2c6f-4e1b-8f4f-7f11c8f2ad2a",
  "type": "service_api",
  "external_user_id": "abc-123",
  "name": "Alice",
  "is_anonymous": false,
  "session_id": "abc-123",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 文件预览

**GET** `/files/:file_id/preview`

预览或下载已上传的文件。此端点允许您访问先前通过文件上传 API 上传的文件。
*文件只能在属于请求应用程序的消息范围内访问。*

### 路径参数

| 参数 | 描述 |
|------|------|
| `file_id` (string) | 要预览的文件的唯一标识符，从文件上传 API 响应中获得。 |

### 查询参数

| 参数 | 描述 |
|------|------|
| `as_attachment` (boolean) | 是否强制将文件作为附件下载。默认为 `false`（在浏览器中预览）。 |

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/files/72fa9618-8f89-4a37-9b33-7e1178a24a67/preview' \
--header 'Authorization: Bearer {api_key}'
```

### 作为附件下载

```bash
curl -X GET 'https://api.dify.ai/v1/files/72fa9618-8f89-4a37-9b33-7e1178a24a67/preview?as_attachment=true' \
--header 'Authorization: Bearer {api_key}' \
--output downloaded_file.png
```

---

## 停止响应

**POST** `/chat-messages/:task_id/stop`

仅支持流式模式。

### 路径参数

| 参数 | 描述 |
|------|------|
| `task_id` (string) | 任务 ID，可在流式返回 Chunk 中获取 |

### Request Body

| 参数 | 描述 |
|------|------|
| `user` (string) | 用户标识，用于定义终端用户的身份，必须和发送消息接口传入 user 保持一致。API 无法访问 WebApp 创建的会话。 |

### 请求示例

```bash
curl -X POST 'https://api.dify.ai/v1/chat-messages/:task_id/stop' \
-H 'Authorization: Bearer {api_key}' \
-H 'Content-Type: application/json' \
--data-raw '{
  "user": "abc-123"
}'
```

### 响应

```json
{
  "result": "success"
}
```

---

## 消息反馈（点赞）

**POST** `/messages/:message_id/feedbacks`

消息终端用户反馈、点赞，方便应用开发者优化输出预期。

### 路径参数

| 参数 | 描述 |
|------|------|
| `message_id` (string) | 消息 ID |

### Request Body

| 参数 | 类型 | 描述 |
|------|------|------|
| `rating` | string | 点赞 `like`, 点踩 `dislike`, 撤销点赞 `null` |
| `user` | string | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |
| `content` | string | 消息反馈的具体信息。 |

### 请求示例

```bash
curl -X POST 'https://api.dify.ai/v1/messages/:message_id/feedbacks' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "rating": "like",
  "user": "abc-123",
  "content": "message feedback information"
}'
```

### 响应

```json
{
  "result": "success"
}
```

---

## 获取 APP 的消息点赞和反馈

**GET** `/app/feedbacks`

获取应用的终端用户反馈、点赞。

### Query 参数

| 参数 | 类型 | 描述 |
|------|------|------|
| `page` | string | （选填）分页，默认值：1 |
| `limit` | string | （选填）每页数量，默认值：20 |

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/app/feedbacks?page=1&limit=20' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json'
```

### 响应示例

```json
{
  "data": [
    {
      "id": "8c0fbed8-e2f9-49ff-9f0e-15a35bdd0e25",
      "app_id": "f252d396-fe48-450e-94ec-e184218e7346",
      "conversation_id": "2397604b-9deb-430e-b285-4726e51fd62d",
      "message_id": "709c0b0f-0a96-4a4e-91a4-ec0889937b11",
      "rating": "like",
      "content": "message feedback information-3",
      "from_source": "user",
      "from_end_user_id": "74286412-9a1a-42c1-929c-01edb1d381d5",
      "from_account_id": null,
      "created_at": "2025-04-24T09:24:38",
      "updated_at": "2025-04-24T09:24:38"
    }
  ]
}
```

---

## 获取下一轮建议问题列表

**GET** `/messages/{message_id}/suggested`

获取下一轮建议问题列表。

### 路径参数

| 参数 | 描述 |
|------|------|
| `message_id` (string) | Message ID |

### Query 参数

| 参数 | 描述 |
|------|------|
| `user` (string) | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |

### 请求示例

```bash
curl --location --request GET 'https://api.dify.ai/v1/messages/{message_id}/suggested?user=abc-123' \
--header 'Authorization: Bearer ENTER-YOUR-SECRET-KEY' \
--header 'Content-Type: application/json'
```

### 响应示例

```json
{
  "result": "success",
  "data": [
    "a",
    "b",
    "c"
  ]
}
```

---

## 获取会话历史消息

**GET** `/messages`

滚动加载形式返回历史聊天记录，第一页返回最新 `limit` 条，即：倒序返回。

### Query 参数

| 参数 | 类型 | 描述 |
|------|------|------|
| `conversation_id` | string | 会话 ID |
| `user` | string | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |
| `first_id` | string | 当前页第一条聊天记录的 ID，默认 null |
| `limit` | int | 一次请求返回多少条聊天记录，默认 20 条。 |

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/messages?user=abc-123&conversation_id={conversation_id}' \
--header 'Authorization: Bearer {api_key}'
```

### 响应示例

```json
{
  "limit": 20,
  "has_more": false,
  "data": [
    {
      "id": "a076a87f-31e5-48dc-b452-0061adbbc922",
      "conversation_id": "cd78daf6-f9e4-4463-9ff2-54257230a0ce",
      "inputs": {
        "name": "dify"
      },
      "query": "iphone 13 pro",
      "answer": "The iPhone 13 Pro, released on September 24, 2021, features a 6.1-inch display...",
      "message_files": [],
      "feedback": null,
      "retriever_resources": [
        {
          "position": 1,
          "dataset_id": "101b4c97-fc2e-463c-90b1-5261a4cdcafb",
          "dataset_name": "iPhone",
          "document_id": "8dd1ad74-0b5f-4175-b735-7d98bbbb4e00",
          "document_name": "iPhone List",
          "segment_id": "ed599c7f-2766-4294-9d1d-e5235a61270a",
          "score": 0.98457545,
          "content": "\"Model\",\"Release Date\",\"Display Size\",\"Resolution\",\"Processor\",\"RAM\",\"Storage\",\"Camera\",\"Battery\",\"Operating System\"\n\"iPhone 13 Pro Max\",\"September 24, 2021\",\"6.7 inch\",\"1284 x 2778\",\"Hexa-core (2x3.23 GHz Avalanche + 4x1.82 GHz Blizzard)\",\"6 GB\",\"128, 256, 512 GB, 1TB\",\"12 MP\",\"4352 mAh\",\"iOS 15"
        }
      ],
      "created_at": 1705569239
    }
  ]
}
```

---

## 获取会话列表

**GET** `/conversations`

获取当前用户的会话列表，默认返回最近的 20 条。

### Query 参数

| 参数 | 类型 | 描述 |
|------|------|------|
| `user` | string | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |
| `last_id` | string | （选填）当前页最后面一条记录的 ID，默认 null |
| `limit` | int | （选填）一次请求返回多少条记录，默认 20 条，最大 100 条，最小 1 条。 |
| `sort_by` | string | （选填）排序字段，默认 -updated_at(按更新时间倒序排列)。可选值：created_at, -created_at, updated_at, -updated_at（-代表倒序）。 |

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/conversations?user=abc-123&last_id=&limit=20' \
--header 'Authorization: Bearer {api_key}'
```

### 响应示例

```json
{
  "limit": 20,
  "has_more": false,
  "data": [
    {
      "id": "10799fb8-64f7-4296-bbf7-b42bfbe0ae54",
      "name": "New chat",
      "inputs": {
        "book": "book",
        "myName": "Lucy"
      },
      "status": "normal",
      "created_at": 1679667915,
      "updated_at": 1679667915
    }
  ]
}
```

---

## 删除会话

**DELETE** `/conversations/:conversation_id`

删除会话。

### 路径参数

| 参数 | 描述 |
|------|------|
| `conversation_id` (string) | 会话 ID |

### Request Body

| 参数 | 描述 |
|------|------|
| `user` (string) | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |

### 请求示例

```bash
curl -X DELETE 'https://api.dify.ai/v1/conversations/{conversation_id}' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer {api_key}' \
--data '{
  "user": "abc-123"
}'
```

### 响应

`204 No Content`

---

## 会话重命名

**POST** `/conversations/:conversation_id/name`

对会话进行重命名，会话名称用于显示在支持多会话的客户端上。

### 路径参数

| 参数 | 描述 |
|------|------|
| `conversation_id` (string) | 会话 ID |

### Request Body

| 参数 | 类型 | 描述 |
|------|------|------|
| `name` | string | （选填）名称，若 `auto_generate` 为 `true` 时，该参数可不传。 |
| `auto_generate` | bool | （选填）自动生成标题，默认 false。 |
| `user` | string | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |

### 请求示例

```bash
curl -X POST 'https://api.dify.ai/v1/conversations/{conversation_id}/name' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {api_key}' \
--data-raw '{
  "name": "",
  "auto_generate": true,
  "user": "abc-123"
}'
```

### 响应

```json
{
  "id": "34d511d5-56de-4f16-a997-57b379508443",
  "name": "hello",
  "inputs": {},
  "status": "normal",
  "introduction": "",
  "created_at": 1732731141,
  "updated_at": 1732734510
}
```

---

## 获取对话变量

**GET** `/conversations/:conversation_id/variables`

从特定对话中检索变量。此端点对于提取对话过程中捕获的结构化数据非常有用。

### 路径参数

| 参数 | 描述 |
|------|------|
| `conversation_id` (string) | 要从中检索变量的对话 ID。 |

### 查询参数

| 参数 | 类型 | 描述 |
|------|------|------|
| `user` | string | 用户标识符，由开发人员定义的规则，在应用程序内必须唯一。 |
| `last_id` | string | （选填）当前页最后面一条记录的 ID，默认 null |
| `limit` | int | （选填）一次请求返回多少条记录，默认 20 条，最大 100 条，最小 1 条。 |

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/conversations/{conversation_id}/variables?user=abc-123' \
--header 'Authorization: Bearer {api_key}'
```

### 带变量名过滤的请求

```bash
curl -X GET 'https://api.dify.ai/v1/conversations/{conversation_id}/variables?user=abc-123&variable_name=customer_name' \
--header 'Authorization: Bearer {api_key}'
```

### 响应示例

```json
{
  "limit": 100,
  "has_more": false,
  "data": [
    {
      "id": "variable-uuid-1",
      "name": "customer_name",
      "value_type": "string",
      "value": "John Doe",
      "description": "客户名称（从对话中提取）",
      "created_at": 1650000000000,
      "updated_at": 1650000000000
    },
    {
      "id": "variable-uuid-2",
      "name": "order_details",
      "value_type": "json",
      "value": "{\"product\":\"Widget\",\"quantity\":5,\"price\":19.99}",
      "description": "客户的订单详情",
      "created_at": 1650000000000,
      "updated_at": 1650000000000
    }
  ]
}
```

---

## 更新对话变量

**PUT** `/conversations/:conversation_id/variables/:variable_id`

更新特定对话变量的值。此端点允许您修改在对话过程中捕获的变量值，同时保留其名称、类型和描述。

### 路径参数

| 参数 | 描述 |
|------|------|
| `conversation_id` (string) | 包含要更新变量的对话 ID。 |
| `variable_id` (string) | 要更新的变量 ID。 |

### 请求体

| 参数 | 类型 | 描述 |
|------|------|------|
| `value` | any | 变量的新值。必须匹配变量的预期类型（字符串、数字、对象等）。 |
| `user` | string | 用户标识符，由开发人员定义的规则，在应用程序内必须唯一。 |

### 请求示例（字符串值）

```bash
curl -X PUT 'https://api.dify.ai/v1/conversations/{conversation_id}/variables/{variable_id}' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {api_key}' \
--data-raw '{
  "value": "Updated Value",
  "user": "abc-123"
}'
```

### 响应

```json
{
  "id": "variable-uuid-1",
  "name": "customer_name",
  "value_type": "string",
  "value": "Updated Value",
  "description": "客户名称（从对话中提取）",
  "created_at": 1650000000000,
  "updated_at": 1650000001000
}
```

---

## 语音转文字

**POST** `/audio-to-text`

### Request Body

该接口需使用 `multipart/form-data` 进行请求。

| 参数 | 类型 | 描述 |
|------|------|------|
| `file` | file | 语音文件。支持格式：`['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']`，文件大小限制：15MB |
| `user` | string | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |

### 请求示例

```bash
curl -X POST 'https://api.dify.ai/v1/audio-to-text' \
--header 'Authorization: Bearer {api_key}' \
--form 'file=@localfile;type=audio/[mp3|mp4|mpeg|mpga|m4a|wav|webm]'
```

### 响应

```json
{
  "text": "hello"
}
```

---

## 文字转语音

**POST** `/text-to-audio`

文字转语音。

### Request Body

| 参数 | 类型 | 描述 |
|------|------|------|
| `message_id` | str | Dify 生成的文本消息，那么直接传递生成的 message-id 即可，后台会通过 message_id 查找相应的内容直接合成语音信息。如果同时传 message_id 和 text，优先使用 message_id。 |
| `text` | str | 语音生成内容。如果没有传 message-id 的话，则会使用这个字段的内容 |
| `user` | string | 用户标识，由开发者定义规则，需保证用户标识在应用内唯一。 |

### 请求示例

```bash
curl -o text-to-audio.mp3 -X POST 'https://api.dify.ai/v1/text-to-audio' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "message_id": "5ad4cb98-f0c7-4085-b384-88c403be6290",
  "text": "Hello Dify",
  "user": "abc-123"
}'
```

### 响应 Headers

```
Content-Type: audio/wav
```

---

## 获取应用基本信息

**GET** `/info`

用于获取应用的基本信息。

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/info' \
-H 'Authorization: Bearer {api_key}'
```

### 响应

```json
{
  "name": "My App",
  "description": "This is my app.",
  "tags": [
    "tag1",
    "tag2"
  ],
  "mode": "advanced-chat",
  "author_name": "Dify"
}
```

---

## 获取应用参数

**GET** `/parameters`

用于进入页面一开始，获取功能开关、输入参数名称、类型及默认值等使用。

### 响应

包含 `opening_statement`, `suggested_questions`, `suggested_questions_after_answer`, `speech_to_text`, `text_to_speech`, `retriever_resource`, `annotation_reply`, `user_input_form`, `file_upload`, `system_parameters` 等。

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/parameters'
```

### 响应示例

```json
{
  "introduction": "nice to meet you",
  "user_input_form": [
    {
      "text-input": {
        "label": "a",
        "variable": "a",
        "required": true,
        "max_length": 48,
        "default": ""
      }
    }
  ],
  "file_upload": {
    "image": {
      "enabled": true,
      "number_limits": 3,
      "transfer_methods": [
        "remote_url",
        "local_file"
      ]
    }
  },
  "system_parameters": {
    "file_size_limit": 15,
    "image_file_size_limit": 10,
    "audio_file_size_limit": 50,
    "video_file_size_limit": 100
  }
}
```

---

## 获取应用 Meta 信息

**GET** `/meta`

用于获取工具 icon。

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/meta' \
-H 'Authorization: Bearer {api_key}'
```

### 响应示例

```json
{
  "tool_icons": {
    "dalle2": "https://cloud.dify.ai/console/api/workspaces/current/tool-provider/builtin/dalle/icon",
    "api_tool": {
      "background": "#252525",
      "content": "😁"
    }
  }
}
```

---

## 获取应用 WebApp 设置

**GET** `/site`

用于获取应用的 WebApp 设置。

### 请求示例

```bash
curl -X GET 'https://api.dify.ai/v1/site' \
-H 'Authorization: Bearer {api_key}'
```

### 响应示例

```json
{
  "title": "My App",
  "chat_color_theme": "#ff4a4a",
  "chat_color_theme_inverted": false,
  "icon_type": "emoji",
  "icon": "😄",
  "icon_background": "#FFEAD5",
  "icon_url": null,
  "description": "This is my app.",
  "copyright": "all rights reserved",
  "privacy_policy": "",
  "custom_disclaimer": "All generated by AI",
  "default_language": "en-US",
  "show_workflow_steps": false,
  "use_icon_as_answer_icon": false
}
```

---

## 标注相关接口

### 获取标注列表

**GET** `/apps/annotations`

#### Query 参数

| 参数 | 类型 | 描述 |
|------|------|------|
| `page` | string | 页码 |
| `limit` | string | 每页数量 |

#### 请求示例

```bash
curl --location --request GET 'https://api.dify.ai/v1/apps/annotations?page=1&limit=20' \
--header 'Authorization: Bearer {api_key}'
```

#### 响应示例

```json
{
  "data": [
    {
      "id": "69d48372-ad81-4c75-9c46-2ce197b4d402",
      "question": "What is your name?",
      "answer": "I am Dify.",
      "hit_count": 0,
      "created_at": 1735625869
    }
  ],
  "has_more": false,
  "limit": 20,
  "total": 1,
  "page": 1
}
```

### 创建标注

**POST** `/apps/annotations`

#### 请求体

| 参数 | 类型 | 描述 |
|------|------|------|
| `question` | string | 问题 |
| `answer` | string | 答案内容 |

#### 请求示例

```bash
curl --location --request POST 'https://api.dify.ai/v1/apps/annotations' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "question": "What is your name?",
  "answer": "I am Dify."
}'
```

#### 响应

```json
{
  "id": "69d48372-ad81-4c75-9c46-2ce197b4d402",
  "question": "What is your name?",
  "answer": "I am Dify.",
  "hit_count": 0,
  "created_at": 1735625869
}
```

### 更新标注

**PUT** `/apps/annotations/{annotation_id}`

#### 路径参数

| 参数 | 描述 |
|------|------|
| `annotation_id` | 标注 ID |

#### 请求体

| 参数 | 描述 |
|------|------|
| `question` | 问题 |
| `answer` | 答案内容 |

#### 请求示例

```bash
curl --location --request PUT 'https://api.dify.ai/v1/apps/annotations/{annotation_id}' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "question": "What is your name?",
  "answer": "I am Dify."
}'
```

#### 响应

同创建标注响应。

### 删除标注

**DELETE** `/apps/annotations/{annotation_id}`

#### 路径参数

| 参数 | 描述 |
|------|------|
| `annotation_id` | 标注 ID |

#### 请求示例

```bash
curl --location --request DELETE 'https://api.dify.ai/v1/apps/annotations/{annotation_id}' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json'
```

#### 响应

`204 No Content`

---

## 标注回复初始设置

### 开启/禁用标注回复

**POST** `/apps/annotation-reply/{action}`

#### 路径参数

| 参数 | 描述 |
|------|------|
| `action` | 只能是 `enable` 或 `disable` |

#### 请求体

| 参数 | 类型 | 描述 |
|------|------|------|
| `embedding_provider_name` | string | 指定的嵌入模型提供商，必须先在系统内设定好接入的模型，对应的是 provider 字段 |
| `embedding_model_name` | string | 指定的嵌入模型，对应的是 model 字段 |
| `score_threshold` | number | 相似度阈值，当相似度大于该阈值时，系统会自动回复，否则不回复 |

#### 请求示例

```bash
curl --location --request POST 'https://api.dify.ai/v1/apps/annotation-reply/{action}' \
--header 'Authorization: Bearer {api_key}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "score_threshold": 0.9,
  "embedding_provider_name": "zhipu",
  "embedding_model_name": "embedding_3"
}'
```

#### 响应（异步任务）

```json
{
  "job_id": "b15c8f68-1cf4-4877-bf21-ed7cf2011802",
  "job_status": "waiting"
}
```

### 查询标注回复初始设置任务状态

**GET** `/apps/annotation-reply/{action}/status/{job_id}`

#### 路径参数

| 参数 | 描述 |
|------|------|
| `action` | 动作，只能是 `enable` 或 `disable`，并且必须和标注回复初始设置接口的动作一致 |
| `job_id` | 任务 ID，从标注回复初始设置接口返回的 job_id |

#### 请求示例

```bash
curl --location --request GET 'https://api.dify.ai/v1/apps/annotation-reply/{action}/status/{job_id}' \
--header 'Authorization: Bearer {api_key}'
```

#### 响应

```json
{
  "job_id": "b15c8f68-1cf4-4877-bf21-ed7cf2011802",
  "job_status": "waiting",
  "error_msg": ""
}
```

---

*以上内容基于 Dify Cloud 提供的 API 文档整理，适用于工作流编排对话型应用。*