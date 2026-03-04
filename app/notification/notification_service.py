# notification_service.py

import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from .firebase_service import send_push_notification
from app.db.repositories.device_repository import DeviceRepository
from app.db.session import SessionLocal
from app.astrology import get_today_nakshatra_end_datetime

# In-memory cache to prevent duplicate notifications
# Key format: (device_token, notification_type, date)
_SENT_CACHE = set()
logger = logging.getLogger("notification")

def _already_sent(device_token: str, notif_type: str, date_str: str) -> bool:
    return (device_token, notif_type, date_str) in _SENT_CACHE


def _mark_sent(device_token: str, notif_type: str, date_str: str):
    _SENT_CACHE.add((device_token, notif_type, date_str))


def send_daily_notifications():
    logging.info("🔔 Running daily notification check")

    db = SessionLocal()

    try:
        devices = DeviceRepository.get_active_devices(db)

        now_utc = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))

        for device in devices:
            # device is ORM object, NOT dict
            try:
                tz = ZoneInfo(device.timezone)
                local_now = now_utc.astimezone(tz)
                today_str = local_now.date().isoformat()

                # logging.info(
                #     f"⏰ Device {device.device_id} local time: {local_now.strftime('%H:%M:%S')}"
                # )

                # -------------------------
                # 🌅 Morning Window (6:00–6:05)
                # -------------------------
                if local_now.hour == 6 and 0 <= local_now.minute <= 5:

                    notif_type = "daily_morning"

                    if not _already_sent(device.fcm_token, notif_type, today_str):

                        send_push_notification(
                            token=device.fcm_token,
                            title="🌙 Daily Nakshatra Update",
                            body="Your nakshatra update is ready.",
                            data={
                                "type": notif_type,
                                "device_id": device.device_id
                            }
                        )

                        _mark_sent(device.fcm_token, notif_type, today_str)
                        logging.info("✅ Morning notification sent")
                    else:
                        logging.info("⚠️ Morning notification already sent")

                # -------------------------
                # ⏳ Nakshatra End Window (±2 min)
                # -------------------------
                nak_end_dt = get_today_nakshatra_end_datetime(
                    lat=device.latitude,
                    lon=device.longitude,
                    timezone_str=device.timezone
                )

                if nak_end_dt:
                    diff_seconds = abs((local_now - nak_end_dt).total_seconds())

                    if diff_seconds <= 120:

                        notif_type = "nakshatra_end"

                        if not _already_sent(device.fcm_token, notif_type, today_str):

                            send_push_notification(
                                token=device.fcm_token,
                                title="⏳ Nakshatra Ending Soon",
                                body="Your current nakshatra is about to end.",
                                data={
                                    "type": notif_type,
                                    "device_id": device.device_id
                                }
                            )

                            _mark_sent(device.fcm_token, notif_type, today_str)
                            logging.info("✅ Nakshatra end notification sent")
                        else:
                            logging.info("⚠️ End notification already sent")
            except ValueError as e:
                if str(e) == "INVALID_FCM_TOKEN":
                    # remove token safely
                    device.device_token = None
                    db.session.commit()

    finally:
        db.close()