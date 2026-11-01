from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.session import Base

class EmergencyAlert(Base):
    """
    SQLAlchemy model representing critical driver risk and emergency response alerts.
    Broadcasts to Caretaker, Hospital, and Police role dashboards.
    """
    __tablename__ = "emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    
    alert_type = Column(String, nullable=False, default="CRITICAL_RISK") # 'CRITICAL_RISK', 'DROWSINESS', 'ACCIDENT', 'PHONE_USE'
    risk_score = Column(Float, nullable=False, default=85.0)
    
    latitude = Column(Float, nullable=True, default=16.5062)
    longitude = Column(Float, nullable=True, default=80.6480)
    
    status = Column(String, nullable=False, default="NEW") # 'NEW', 'ACKNOWLEDGED', 'RESPONDING', 'RESOLVED'
    details = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    driver = relationship("User", backref="emergency_alerts")
    vehicle = relationship("Vehicle", backref="emergency_alerts")
