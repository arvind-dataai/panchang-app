import logging
from datetime import datetime

def send_push_notification(token: str, title: str, body: str, data: dict | None = None):
    logging.info("📲 MOCK FCM SEND")
    logging.info(f"Token: {token}")
    logging.info(f"Title: {title}")
    logging.info(f"Body: {body}")

    if data:
        logging.info(f"Data Payload: {data}")

    logging.info(f"Sent at: {datetime.utcnow().isoformat()}")