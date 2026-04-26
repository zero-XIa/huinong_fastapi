from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Session(Base):
    __tablename__ = "tb_session"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("tb_user.id"), nullable=False)
    session_id = Column(String(64), unique=True, nullable=False)  # 前端使用的会话标识
    dify_conversation_id = Column(String(64))  # Dify 返回的 conversation_id
    title = Column(String(100))  # 会话标题
    last_message_time = Column(DateTime, server_default=func.now())
    create_time = Column(DateTime, server_default=func.now())