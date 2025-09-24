"""
Message processing background tasks.
"""
from celery import current_task
from app.core.celery import celery_app
from app.database import SessionLocal
from app.models.message import Message, MessageStatus
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_message_status_update(self, message_id: int, status: str):
    """
    Update message status (sent, delivered, read, failed).
    """
    db = SessionLocal()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return {"status": "failed", "error": "Message not found"}
        
        # Update message status
        message.update_status(MessageStatus(status))
        db.commit()
        
        logger.info(f"Updated message {message_id} status to {status}")
        return {"status": "completed", "message_id": message_id, "new_status": status}
        
    except Exception as e:
        logger.error(f"Error updating message status: {e}")
        db.rollback()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def retry_failed_messages(self):
    """
    Retry failed message deliveries.
    """
    db = SessionLocal()
    try:
        # Find messages that failed and can be retried
        failed_messages = db.query(Message).filter(
            Message.status == MessageStatus.FAILED,
            Message.direction == "outbound"
        ).all()
        
        retry_count = 0
        for message in failed_messages:
            try:
                # TODO: Implement actual message retry logic
                # This will be expanded in Phase 2 when we implement WhatsApp integration
                logger.info(f"Retrying message {message.id} to {message.contact_id}")
                retry_count += 1
            except Exception as e:
                logger.error(f"Error retrying message {message.id}: {e}")
        
        return {
            "status": "completed",
            "messages_retried": retry_count,
            "total_failed": len(failed_messages)
        }
        
    except Exception as e:
        logger.error(f"Error in retry failed messages: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
