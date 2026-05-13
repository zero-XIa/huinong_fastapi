from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Message(Base):
    __tablename__ = "tb_message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("tb_user.id"), nullable=False)
    session_id = Column(String(64), index=True, nullable=False)
    role = Column(String(20), nullable=False) # user 或 ai
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    create_time = Column(DateTime, server_default=func.now())
