from pydantic import BaseModel
from typing import Optional

class VehicleCreate(BaseModel):
    manufacturer: str = "Toyota"
    model_name: str = "Innova Crysta"
    variant: Optional[str] = "2.8Z AT"
    year: int = 2024
    license_plate: str = "KA-01-MJ-9999"
    color: Optional[str] = "Pearl White"
    fuel_type: Optional[str] = "Diesel"
    vin: Optional[str] = None

class VehicleUpdate(BaseModel):
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    variant: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None
    color: Optional[str] = None
    fuel_type: Optional[str] = None
    vin: Optional[str] = None

class VehicleResponse(BaseModel):
    id: int
    user_id: int
    manufacturer: str
    model_name: str
    variant: Optional[str]
    year: int
    license_plate: str
    color: Optional[str]
    fuel_type: Optional[str]
    vin: Optional[str]

    class Config:
        from_attributes = True
