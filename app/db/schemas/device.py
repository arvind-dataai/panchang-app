from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---------- REQUEST SCHEMAS ----------

class DeviceRegisterRequest(BaseModel):
    device_id: str
    platform: str
    timezone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fcm_token: Optional[str] = None


class DeviceHeartbeatRequest(BaseModel):
    device_id: str
    timezone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fcm_token: Optional[str] = None


# ---------- RESPONSE SCHEMA ----------

class DeviceResponse(BaseModel):
    device_id: str
    platform: str
    timezone: str
    latitude: Optional[float]
    longitude: Optional[float]
    is_active: bool
    last_seen_at: datetime

    class Config:
        from_attributes = True