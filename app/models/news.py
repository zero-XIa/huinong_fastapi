from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.base import Base

class News(Base):
    __tablename__ = "tb_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # 存储 Markdown 或 HTML
    category = Column(String(50))           # 政策、预警、农技
    cover_url = Column(String(500))         # 封面图地址
    publish_time = Column(DateTime, default=datetime.now)
    view_count = Column(Integer, default=0)