from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    """
    SQLAlchemy model representing the user accounts.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, default="driver", nullable=False)
    is_active = Column(Boolean, default=True)

    telemetry_records = relationship("Telemetry", back_populates="user", cascade="all, delete-orphan")

