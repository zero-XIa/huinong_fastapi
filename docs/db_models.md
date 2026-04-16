极简的格式列出所有数据表及其核心字段、类型、约束，供 AI 快速理解数据库结构，用于生成 SQLAlchemy 模型、CRUD 代码等。
# 慧农数据库表结构（精简版）
## tb_user
- id: int PK
- username: str(50) unique not null
- password: str(128) not null
- phone: str(20) unique
- elder_mode: bool default false
- role: str(20) default 'user'   # user/admin
- create_time: datetime default now
## tb_news
- id: int PK
- title: str(200) not null
- content: text not null
- category: str(50)
- cover_url: str(500)
- publish_time: datetime default now
- view_count: int default 0
- is_deleted: bool default false
## tb_crop
- id: int PK
- crop_name: str(50) not null
- description: text
## tb_identification
- id: int PK
- user_id: int FK -> tb_user.id
- crop_id: int FK -> tb_crop.id (可选)
- image_url: str(255) not null
- disease_name: str(100)
- advice: text
- confidence: float
- duration: int
- create_time: datetime default now
## tb_message
- id: int PK
- user_id: int FK -> tb_user.id
- session_id: str(64) not null index   # 关联 tb_session.session_id
- role: str(20) not null               # user/ai
- content: text not null
- create_time: datetime default now
## tb_session (新增)
- id: int PK
- user_id: int FK -> tb_user.id
- session_id: str(64) unique not null  # 前端使用的会话标识
- dify_conversation_id: str(64)        # Dify 返回的 conversation_id
- title: str(100)                      # 会话标题
- last_message_time: datetime default now
- create_time: datetime default now