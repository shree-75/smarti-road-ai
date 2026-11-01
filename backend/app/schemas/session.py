from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DriverSessionCreate(BaseModel):
    pass

class DriverSessionEnd(BaseModel):
    average_risk_score: Optional[float] = 0.0
    max_risk_score: Optional[float] = 0.0
    total_drowsy_events: Optional[int] = 0
    total_distracted_events: Optional[int] = 0
    total_yawn_events: Optional[int] = 0
    total_phone_events: Optional[int] = 0
    total_drinking_events: Optional[int] = 0
    seatbelt_status: Optional[str] = "UNKNOWN"
    attention_percentage: Optional[float] = 100.0

class DriverSessionResponse(BaseModel):
    id: int
    user_id: int
    session_code: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_sec: float
    status: str
    average_risk_score: float
    max_risk_score: float
    total_drowsy_events: int
    total_distracted_events: int
    total_yawn_events: int
    total_phone_events: int
    total_drinking_events: int
    seatbelt_status: Optional[str] = "N/A"
    attention_percentage: float

    class Config:
        from_attributes = True
