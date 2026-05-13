from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Literal

NEWS_CATEGORIES = Literal["政策", "农技", "市场", "预警"]


class NewsBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    category: NEWS_CATEGORIES = Field(description="资讯分类：政策、预警、农技")
    cover_url: Optional[str] = None


class NewsCreate(NewsBase):
    publish_time: Optional[datetime] = None


class NewsResponse(NewsBase):
    id: int
    publish_time: datetime
    view_count: int

    model_config = ConfigDict(from_attributes=True)
