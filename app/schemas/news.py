from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class NewsBase(BaseModel):
    title: str
    content: str
    category: str
    cover_url: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class NewsResponse(NewsBase):
    id: int
    publish_time: datetime
    view_count: int

    model_config = ConfigDict(from_attributes=True) # 允许从 ORM 对象转换