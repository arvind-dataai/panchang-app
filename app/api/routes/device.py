from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.schemas.device import DeviceRegisterRequest, DeviceResponse,DeviceHeartbeatRequest
from app.db.services.device_service import DeviceService

router = APIRouter(prefix="/device", tags=["Device"])


@router.post("/register", response_model=DeviceResponse)
def register_device(
    payload: DeviceRegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        device = DeviceService.register_or_update_device(
            db=db,
            device_id=payload.device_id,
            platform=payload.platform,
            timezone=payload.timezone,
            latitude=payload.latitude,
            longitude=payload.longitude,
            fcm_token=payload.fcm_token
        )
        return device
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/heartbeat", response_model=DeviceResponse)
def device_heartbeat(
    payload: DeviceHeartbeatRequest,
    db: Session = Depends(get_db)
):
    """
    Called periodically by app to update:
    - last_seen_at
    - location
    - timezone
    - fcm_token
    """

    device = DeviceService.register_or_update_device(
        db=db,
        device_id=payload.device_id,
        platform="unknown",  # platform not updated here
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        fcm_token=payload.fcm_token
    )

    return device
