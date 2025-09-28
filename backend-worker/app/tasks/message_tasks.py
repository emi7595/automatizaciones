"""
Message processing background tasks.
Uses backend API instead of direct database access.
"""
from celery import current_task
from app.core.celery import celery_app
from app.core.api_client import send_message_to_contact, get_message, update_message_status
from app.core.logging import get_logger, log_performance
import asyncio

logger = get_logger(__name__)


@celery_app.task(bind=True)
@log_performance()
def process_message_status_update(self, whatsapp_message_id: str, status: str, timestamp: int = None):
    """
    Update message status from WhatsApp webhook data.
    Uses backend API to update message status.
    """
    logger.info(f"Processing message status update: {whatsapp_message_id} -> {status}")
    logger.debug(f"Timestamp: {timestamp}")
    
    try:
        # Update message status via backend API
        result = asyncio.run(update_message_status(whatsapp_message_id, status, timestamp))
        
        if result.get("success"):
            logger.info(f"Updated message status: {whatsapp_message_id} -> {status}")
            return {
                "status": "completed",
                "message_id": result.get("message_id"),
                "old_status": result.get("old_status"),
                "new_status": status
            }
        else:
            logger.error(f"Failed to update message status: {result.get('error')}")
            return {"status": "failed", "error": result.get("error")}
        
    except Exception as e:
        logger.error(f"Error updating message status: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
@log_performance()
def send_whatsapp_message(self, contact_id: int, content: str, message_type: str = "text", user_id: int = None):
    """
    Send WhatsApp message to contact via backend API.
    """
    logger.info(f"Sending WhatsApp message to contact {contact_id}: {content[:50]}...")
    
    try:
        # Send message via backend API
        result = asyncio.run(send_message_to_contact(contact_id, content, message_type, user_id))
        
        if result.get("success"):
            logger.info(f"Message sent successfully to contact {contact_id}")
            return {
                "status": "completed",
                "contact_id": contact_id,
                "message_id": result.get("message_id"),
                "whatsapp_message_id": result.get("whatsapp_message_id")
            }
        else:
            logger.error(f"Failed to send message to contact {contact_id}: {result.get('error')}")
            return {"status": "failed", "error": result.get("error")}
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
@log_performance()
def retry_failed_messages(self):
    """
    Retry failed message deliveries via backend API.
    """
    logger.info("Retrying failed messages")
    
    try:
        # Get failed messages from backend API
        result = asyncio.run(get_failed_messages())
        
        if not result.get("success"):
            logger.error(f"Failed to get failed messages: {result.get('error')}")
            return {"status": "failed", "error": result.get("error")}
        
        failed_messages = result.get("messages", [])
        retry_count = 0
        
        for message in failed_messages:
            try:
                # Retry sending the message
                retry_result = asyncio.run(send_message_to_contact(
                    message["contact_id"],
                    message["content"],
                    message.get("message_type", "text"),
                    message.get("user_id")
                ))
                
                if retry_result.get("success"):
                    retry_count += 1
                    logger.info(f"Successfully retried message {message['id']}")
                else:
                    logger.error(f"Failed to retry message {message['id']}: {retry_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error retrying message {message['id']}: {str(e)}")
        
        logger.info(f"Retried {retry_count}/{len(failed_messages)} failed messages")
        return {
            "status": "completed",
            "messages_retried": retry_count,
            "total_failed": len(failed_messages)
        }
        
    except Exception as e:
        logger.error(f"Error in retry_failed_messages: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}
