from sqlalchemy.orm import Session
from app.db.models.device import Device


class DeviceRepository:

    @staticmethod
    def create_device(db: Session, device: Device) -> Device:
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def get_device_by_device_id(db: Session, device_id: str) -> Device | None:
        return (
            db.query(Device)
            .filter(Device.device_id == device_id)
            .first()
        )

    @staticmethod
    def update_device(db: Session, device: Device) -> Device:
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def get_active_devices(db: Session) -> list[Device]:
        return (
            db.query(Device)
            .filter(
                Device.is_active == True,
                Device.fcm_token.isnot(None)
            )
            .all()
        )
