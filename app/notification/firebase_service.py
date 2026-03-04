import firebase_admin
from firebase_admin import credentials, messaging
import logging
import os
from datetime import datetime

logger = logging.getLogger("firebase")
# ---- Initialize Firebase only once ----
_FIREBASE_APP = None
FIREBASE_SERVICE_ACCOUNT = "/Users/arvind/Desktop/Utkarsh/nakshatra/google-services.json"
def _initialize_firebase():
    global _FIREBASE_APP

    if _FIREBASE_APP:
        return _FIREBASE_APP

    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if not service_account_path:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT env variable not set")

    cred = credentials.Certificate(service_account_path)
    _FIREBASE_APP = firebase_admin.initialize_app(cred)

    logging.info("🔥 Firebase initialized successfully")
    return _FIREBASE_APP


def send_push_notification(token: str, title: str, body: str, data: dict | None = None):
    """
    Sends real push notification via Firebase Cloud Messaging
    """

    try:
        _initialize_firebase()

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
            data=data or {}
        )

        response = messaging.send(message)

        logging.info("📲 FCM SENT SUCCESS")
        logging.info(f"Message ID: {response}")
        logging.info(f"Sent at: {datetime.utcnow().isoformat()}")

    except messaging.UnregisteredError:
        logging.warning(f"FCM invalid token detected: {token}")
        raise ValueError("INVALID_FCM_TOKEN")

    except Exception as e:
        logging.error("❌ FCM SEND FAILED")
        logging.error(str(e))