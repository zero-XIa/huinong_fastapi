from pydantic import BaseModel
from typing import Optional

class IdentifyResponse(BaseModel):
    disease_name: str
    advice: str
    confidence: float