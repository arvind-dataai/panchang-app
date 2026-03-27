import firebase_admin
from firebase_admin import credentials, messaging
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger("firebase")
# ---- Initialize Firebase only once ----
_FIREBASE_APP = None

load_dotenv()


def _initialize_firebase():
    global _FIREBASE_APP

    if _FIREBASE_APP:
        return _FIREBASE_APP

    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if not service_account_path:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT env variable not set")

    cred = credentials.Certificate(service_account_path)
    _FIREBASE_APP = firebase_admin.initialize_app(cred)

    logger.info("Firebase initialized and ready")
    return _FIREBASE_APP


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: dict | None = None,
    image_url: str | None = None,
):
    """
    Sends real push notification via Firebase Cloud Messaging
    """

    try:
        _initialize_firebase()

        data = {k: str(v) for k, v in (data or {}).items() if v is not None}

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image_url,
            ),
            token=token,
            data=data,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="default",
                    sound="default",
                    color="#F39C12",
                    image=image_url,
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        mutable_content=True,
                    )
                )
            ),
        )

        response = messaging.send(message)
        return response

    except messaging.UnregisteredError:
        logger.warning("FCM invalid token detected")
        raise ValueError("INVALID_FCM_TOKEN")

    except Exception as e:
        logger.error("FCM send failed in firebase_service.send_push_notification: %s", e)
        return None
