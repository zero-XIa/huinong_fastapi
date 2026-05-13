from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class News(Base):
    __tablename__ = "tb_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    cover_url = Column(String(500))
    publish_time = Column(DateTime, server_default=func.now())
    view_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)