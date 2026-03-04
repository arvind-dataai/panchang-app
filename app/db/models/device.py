from sqlalchemy import Column, String, Boolean, DateTime, Float
from datetime import datetime
from app.db.base import Base

class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)
    fcm_token = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String, nullable=False)
    platform = Column(String, nullable=False)  # android / ios
    is_active = Column(Boolean, default=True)

    last_seen_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )