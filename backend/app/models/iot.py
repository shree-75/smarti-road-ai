from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.db.session import Base

class IoTTelemetry(Base):
    """
    SQLAlchemy model for ESP32 IoT hardware sensor telemetry.
    Persists MAX30102 (heart_rate, spo2), MPU6050 (accel, gyro), MQ (alcohol), SW-420 (vibration).
    """
    __tablename__ = "iot_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, default="ESP32-001", index=True)
    esp32_ip = Column(String, nullable=True)
    session_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Biometric & Sensor Data
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    alcohol = Column(Float, nullable=True)
    vibration = Column(Integer, default=0)

    # MPU6050 Accelerometer & Gyroscope
    acceleration_x = Column(Float, default=0.0)
    acceleration_y = Column(Float, default=0.0)
    acceleration_z = Column(Float, default=1.0)
    gyro_x = Column(Float, default=0.0)
    gyro_y = Column(Float, default=0.0)
    gyro_z = Column(Float, default=0.0)

    # Sensor Availability Metadata Map
    sensor_statuses = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "esp32_ip": self.esp32_ip,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "heart_rate": self.heart_rate,
            "spo2": self.spo2,
            "alcohol": self.alcohol,
            "vibration": self.vibration,
            "acceleration_x": self.acceleration_x,
            "acceleration_y": self.acceleration_y,
            "acceleration_z": self.acceleration_z,
            "gyro_x": self.gyro_x,
            "gyro_y": self.gyro_y,
            "gyro_z": self.gyro_z,
            "sensors": self.sensor_statuses or {
                "max30102": "ONLINE" if self.heart_rate is not None else "OFFLINE",
                "mpu6050": "ONLINE",
                "alcohol": "ONLINE" if self.alcohol is not None else "OFFLINE",
                "vibration": "ONLINE"
            },
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
