from app.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def send_offline_notification(self, user_email: str, username: str, room_name: str, message_content: str):
    try:
        # In production replace with real SMTP
        logger.info(f"Sending email to {user_email}")
        logger.info(f"Hey {username}, you missed a message in {room_name}: {message_content[:50]}")
        return {"status": "sent", "email": user_email}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)