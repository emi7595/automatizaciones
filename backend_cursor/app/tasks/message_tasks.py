"""
Message processing background tasks.
"""
from celery import current_task
from app.core.celery import celery_app
from app.database import SessionLocal
from app.models.message import Message, MessageStatus
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)


@celery_app.task(bind=True)
@log_performance()
def process_message_status_update(self, whatsapp_message_id: str, status: str, timestamp: int = None):
    """
    Update message status from WhatsApp webhook data.
    """
    logger.info(f"Processing message status update: {whatsapp_message_id} -> {status}")
    logger.debug(f"Timestamp: {timestamp}")
    
    db = SessionLocal()
    try:
        message = db.query(Message).filter(Message.whatsapp_message_id == whatsapp_message_id).first()
        if not message:
            logger.error(f"Message not found: {whatsapp_message_id}")
            return {"status": "failed", "error": "Message not found"}
        
        # Update message status
        old_status = message.status
        message.update_status(MessageStatus(status), timestamp)
        db.commit()
        
        logger.info(f"Updated message {message.id} status from {old_status} to {status}")
        return {"status": "completed", "message_id": message.id, "old_status": old_status, "new_status": status}
        
    except Exception as e:
        logger.error(f"Error updating message status: {str(e)}")
        logger.exception("Full error traceback:")
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
                logger.error(f"Error retrying message {message.id}: {str(e)}")
        
        return {
            "status": "completed",
            "messages_retried": retry_count,
            "total_failed": len(failed_messages)
        }
        
    except Exception as e:
        logger.error(f"Error in retry failed messages: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
