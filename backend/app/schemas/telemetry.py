from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class TelemetryBase(BaseModel):
    speed: Optional[float] = Field(None, ge=0, description="Vehicle speed in km/h")
    heart_rate: Optional[float] = Field(None, ge=0, le=300, description="Driver heart rate in BPM")
    spo2: Optional[float] = Field(None, ge=0, le=100, description="Driver oxygen saturation percentage")
    alcohol_level: Optional[float] = Field(None, ge=0, description="Alcohol sensor reading")
    acceleration: Optional[float] = Field(None, description="Vehicle acceleration / G-force")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    driver_status: Optional[str] = Field("normal", description="Driver status e.g. normal, drowsy, alert")

class TelemetryCreate(TelemetryBase):
    timestamp: Optional[datetime] = None

class TelemetryResponse(TelemetryBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
