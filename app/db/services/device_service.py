from sqlalchemy.orm import Session
from app.db.models.device import Device
from app.db.repositories.device_repository import DeviceRepository
from datetime import datetime


class DeviceService:

    @staticmethod
    def register_or_update_device(
        db: Session,
        device_id: str,
        platform: str,
        timezone: str,
        fcm_token: str,
        latitude: float | None = None,
        longitude: float | None = None,
        
    ) -> Device:

        existing_device = DeviceRepository.get_device_by_device_id(
            db=db,
            device_id=device_id
        )

        if existing_device:
            # Update existing device
            existing_device.platform = platform
            existing_device.timezone = timezone
            existing_device.fcm_token = fcm_token 
            existing_device.latitude = latitude
            existing_device.longitude = longitude
            existing_device.last_seen_at = datetime.utcnow()

            return DeviceRepository.update_device(db, existing_device)

        # Create new device
        new_device = Device(
            device_id=device_id,
            platform=platform,
            timezone=timezone,
            fcm_token=fcm_token,
            latitude=latitude,
            longitude=longitude,
            last_seen_at=datetime.utcnow()
        )

        return DeviceRepository.create_device(db, new_device)
