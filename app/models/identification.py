from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Identification(Base):
    __tablename__ = "tb_identification"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("tb_user.id"), nullable=False)
    image_url = Column(String(255), nullable=False)
    crop_name = Column(String(50), nullable=True)
    disease_name = Column(String(100), nullable=True)
    advice = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)
    create_time = Column(DateTime, server_default=func.now())
