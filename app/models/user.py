from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "tb_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    phone = Column(String(20), unique=True)
    create_time = Column(DateTime, server_default=func.now())
    elder_mode = Column(Boolean, default=False)
    role = Column(String(20), default='user')