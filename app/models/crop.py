from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Crop(Base):
    __tablename__ = "tb_crop"
    id = Column(Integer, primary_key=True)
    crop_name = Column(String(50), nullable=False)
    description = Column(Text)

class Identification(Base):
    __tablename__ = "tb_identification"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("tb_user.id"))
    crop_id = Column(Integer, ForeignKey("tb_crop.id"))
    image_url = Column(String(255), nullable=False)
    disease_name = Column(String(100))
    advice = Column(Text) # 对应你的结构化防治建议设计
    confidence = Column(Float)
    duration = Column(Integer)
    create_time = Column(DateTime, server_default=func.now())

class Message(Base):
    __tablename__ = "tb_message"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("tb_user.id"))
    session_id = Column(String(64), index=True, nullable=False)
    role = Column(String(20), nullable=False) # user / ai
    content = Column(Text, nullable=False)
    create_time = Column(DateTime, server_default=func.now())