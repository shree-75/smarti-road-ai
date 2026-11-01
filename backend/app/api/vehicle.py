from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.get("/", response_model=List[VehicleResponse])
def get_user_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all vehicles belonging to the authenticated driver.
    """
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == current_user.id).all()
    if not vehicles:
        # Create a default vehicle if none exists yet
        default_v = Vehicle(
            user_id=current_user.id,
            manufacturer="Toyota",
            model_name="Innova Crysta",
            variant="2.8Z AT",
            year=2024,
            license_plate="KA-01-MJ-9999",
            color="Pearl White",
            fuel_type="Diesel"
        )
        db.add(default_v)
        db.commit()
        db.refresh(default_v)
        return [default_v]
    return vehicles

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new vehicle record for the current user.
    """
    vehicle = Vehicle(
        user_id=current_user.id,
        **payload.model_dump()
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing vehicle record owned by the authenticated user.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.user_id == current_user.id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized access.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a vehicle record owned by the current user.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.user_id == current_user.id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized access.")

    db.delete(vehicle)
    db.commit()
    return None
