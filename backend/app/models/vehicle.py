from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base

class Vehicle(Base):
    """
    SQLAlchemy model representing driver vehicle profile.
    Stores car manufacturer, model name, variant, manufacturing year, and registration details.
    """
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    manufacturer = Column(String, nullable=False, default="Toyota")
    model_name = Column(String, nullable=False, default="Innova Crysta")
    variant = Column(String, nullable=True, default="2.8Z AT")
    year = Column(Integer, nullable=False, default=2024)
    license_plate = Column(String, nullable=False, default="KA-01-MJ-9999")
    color = Column(String, nullable=True, default="Pearl White")
    fuel_type = Column(String, nullable=True, default="Diesel")
    vin = Column(String, nullable=True)

    user = relationship("User", backref="vehicles")
