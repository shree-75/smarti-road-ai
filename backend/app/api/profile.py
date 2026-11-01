from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.profile import DriverProfile
from app.schemas.profile import DriverProfileUpdate, DriverProfileResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/profiles", tags=["driver-profiles"])

@router.get("/me", response_model=DriverProfileResponse)
def get_current_driver_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves or initializes the personalized calibration profile for the authenticated driver.
    """
    profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not profile:
        profile = DriverProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.post("/me", response_model=DriverProfileResponse)
def update_current_driver_profile(
    profile_in: DriverProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates or saves personalized baseline calibration statistics for the authenticated driver.
    """
    profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not profile:
        profile = DriverProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)
    return profile
