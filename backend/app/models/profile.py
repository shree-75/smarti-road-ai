from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.session import Base

class DriverProfile(Base):
    """
    SQLAlchemy model representing a driver's personalized statistical calibration profile.
    Stores baseline mean and standard deviation parameters across eye, mouth, and head pose metrics.
    """
    __tablename__ = "driver_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    ear_baseline_mean = Column(Float, default=0.310, nullable=False)
    ear_baseline_std = Column(Float, default=0.030, nullable=False)
    
    mar_baseline_mean = Column(Float, default=0.180, nullable=False)
    mar_baseline_std = Column(Float, default=0.040, nullable=False)
    
    yaw_baseline_mean = Column(Float, default=0.0, nullable=False)
    yaw_baseline_std = Column(Float, default=5.0, nullable=False)
    
    pitch_baseline_mean = Column(Float, default=0.0, nullable=False)
    pitch_baseline_std = Column(Float, default=5.0, nullable=False)
    
    roll_baseline_mean = Column(Float, default=0.0, nullable=False)
    roll_baseline_std = Column(Float, default=3.0, nullable=False)
    
    calibration_samples = Column(Integer, default=0, nullable=False)
    is_calibrated = Column(Boolean, default=False, nullable=False)
    
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="driver_profile", uselist=False)
