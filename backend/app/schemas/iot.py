from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from datetime import datetime

class IoTTelemetryCreate(BaseModel):
    device_id: Optional[str] = "ESP32-001"
    esp32_ip: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[Union[str, int, float]] = None
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    alcohol: Optional[float] = None
    vibration: Optional[int] = 0
    acceleration_x: Optional[float] = None
    acceleration_y: Optional[float] = None
    acceleration_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    sensors: Optional[Dict[str, str]] = None

class IoTTelemetryResponse(BaseModel):
    id: int
    device_id: str
    esp32_ip: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[Union[str, int, float]] = None
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    alcohol: Optional[float] = None
    vibration: Optional[int] = 0
    acceleration_x: Optional[float] = None
    acceleration_y: Optional[float] = None
    acceleration_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    sensors: Dict[str, str]
    created_at: str

    class Config:
        from_attributes = True

class IoTStatusResponse(BaseModel):
    connected: bool
    device_id: str
    esp32_ip: Optional[str] = None
    last_seen_sec: Optional[float] = None
    sensor_statuses: Dict[str, str]

class IoTNetworkInfoResponse(BaseModel):
    server_ip: str
    server_port: int
    telemetry_url: str
    frontend_url: str
    status: str

class IoTConfigResponse(BaseModel):
    server_ip: str
    server_port: int
    telemetry_path: str
    telemetry_url: str
