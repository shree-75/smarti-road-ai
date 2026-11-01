from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.session import Base

class DriverSession(Base):
    """
    SQLAlchemy model representing a driving/monitoring session.
    Stores aggregate safety statistics, session duration, and safety event counts.
    """
    __tablename__ = "driver_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_code = Column(String, unique=True, index=True, nullable=False)
    
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_sec = Column(Float, default=0.0, nullable=False)
    
    status = Column(String, default="active", nullable=False) # 'active', 'completed'
    
    average_risk_score = Column(Float, default=0.0, nullable=False)
    max_risk_score = Column(Float, default=0.0, nullable=False)
    
    total_drowsy_events = Column(Integer, default=0, nullable=False)
    total_distracted_events = Column(Integer, default=0, nullable=False)
    total_yawn_events = Column(Integer, default=0, nullable=False)
    total_phone_events = Column(Integer, default=0, nullable=False)
    total_drinking_events = Column(Integer, default=0, nullable=False)
    
    seatbelt_status = Column(String, default="UNKNOWN", nullable=False)
    attention_percentage = Column(Float, default=100.0, nullable=False)

    user = relationship("User", backref="driver_sessions")
