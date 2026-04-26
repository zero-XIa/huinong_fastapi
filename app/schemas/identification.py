from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class IdentificationBase(BaseModel):
    image_url: str
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    advice: Optional[str] = None
    confidence: Optional[float] = None
    duration: Optional[int] = None

class IdentificationCreate(IdentificationBase):
    pass

class IdentificationUpdate(BaseModel):
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    advice: Optional[str] = None
    confidence: Optional[float] = None
    duration: Optional[int] = None

class IdentificationInDB(IdentificationBase):
    id: int
    user_id: int
    create_time: datetime

    class Config:
        from_attributes = True

class Identification(IdentificationInDB):
    pass

class IdentificationHistory(BaseModel):
    id: int
    image_url: str
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    confidence: Optional[float] = None
    create_time: datetime

class IdentificationHistoryDetail(Identification):
    pass

class IdentificationResponse(BaseModel):
    id: int
    image_url: str
    crop_name: Optional[str] = None
    disease_name: str
    advice: str
    confidence: float
    duration: int
    create_time: datetime
