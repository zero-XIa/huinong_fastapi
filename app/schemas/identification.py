from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# 识别记录的基础字段，增删改查都共用这一套字段定义
class IdentificationBase(BaseModel):
    image_url: str
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    characteristics: Optional[str] = None          # 病害特征描述，Dify 工作流返回
    confidence: Optional[float] = None
    duration: Optional[int] = None                  # Dify 调用耗时，单位毫秒


# 新增识别记录时用，直接复用基础字段
class IdentificationCreate(IdentificationBase):
    pass


# 更新识别记录，所有字段都可选（目前没地方调这个接口，先留着）
class IdentificationUpdate(BaseModel):
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    characteristics: Optional[str] = None
    confidence: Optional[float] = None
    duration: Optional[int] = None


# 从数据库查出来时的完整结构，带上 id、user_id、create_time
class IdentificationInDB(IdentificationBase):
    id: int
    user_id: int
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)


# 对外暴露的完整识别记录
class Identification(IdentificationInDB):
    pass


# 历史列表用，只展示缩略信息，不加 characteristics（太长了）
class IdentificationHistory(BaseModel):
    id: int
    image_url: str
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    confidence: Optional[float] = None
    create_time: datetime


# 历史记录的详情页复用完整 Identification
class IdentificationHistoryDetail(Identification):
    pass


# /crops/identify 接口的返回结构，字段都是必填的（前端直接展示）
class IdentificationResponse(BaseModel):
    id: int
    image_url: str
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    characteristics: Optional[str] = None
    confidence: Optional[float] = None
    duration: int
    create_time: datetime
