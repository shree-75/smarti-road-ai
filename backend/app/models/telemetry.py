from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.session import Base

class Telemetry(Base):
    """
    SQLAlchemy model representing telemetry records captured from driver sensors.
    """
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    speed = Column(Float, nullable=True)
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    alcohol_level = Column(Float, nullable=True)
    acceleration = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    driver_status = Column(String, default="normal", nullable=True)

    user = relationship("User", back_populates="telemetry_records")
