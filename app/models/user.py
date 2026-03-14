from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "tb_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    phone = Column(String(20), unique=True)
    elder_mode = Column(Boolean, default=False) # 对应你的长辈模式设计
    create_time = Column(DateTime, server_default=func.now())