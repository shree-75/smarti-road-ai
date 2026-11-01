from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmergencyAlertCreate(BaseModel):
    alert_type: str = "CRITICAL_RISK"
    risk_score: float = 85.0
    latitude: Optional[float] = 16.5062
    longitude: Optional[float] = 80.6480
    details: Optional[str] = None
    vehicle_id: Optional[int] = None

class EmergencyAlertStatusUpdate(BaseModel):
    status: str # 'NEW', 'ACKNOWLEDGED', 'RESPONDING', 'RESOLVED'

class EmergencyAlertResponse(BaseModel):
    id: int
    driver_id: int
    vehicle_id: Optional[int]
    alert_type: str
    risk_score: float
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    details: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
