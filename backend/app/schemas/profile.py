from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DriverProfileUpdate(BaseModel):
    ear_baseline_mean: Optional[float] = None
    ear_baseline_std: Optional[float] = None
    mar_baseline_mean: Optional[float] = None
    mar_baseline_std: Optional[float] = None
    yaw_baseline_mean: Optional[float] = None
    yaw_baseline_std: Optional[float] = None
    pitch_baseline_mean: Optional[float] = None
    pitch_baseline_std: Optional[float] = None
    roll_baseline_mean: Optional[float] = None
    roll_baseline_std: Optional[float] = None
    calibration_samples: Optional[int] = None
    is_calibrated: Optional[bool] = None

class DriverProfileResponse(BaseModel):
    id: int
    user_id: int
    ear_baseline_mean: float
    ear_baseline_std: float
    mar_baseline_mean: float
    mar_baseline_std: float
    yaw_baseline_mean: float
    yaw_baseline_std: float
    pitch_baseline_mean: float
    pitch_baseline_std: float
    roll_baseline_mean: float
    roll_baseline_std: float
    calibration_samples: int
    is_calibrated: bool
    updated_at: datetime

    class Config:
        from_attributes = True
