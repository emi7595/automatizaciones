"""
Task queue helper for backend API to communicate with worker services.
This module provides a clean interface for queuing tasks to the worker.
"""
from app.core.celery import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


class TaskQueue:
    """Helper class for queuing tasks to worker services."""
    
    @staticmethod
    def queue_message_automation(message_id: int):
        """Queue message automation task for worker."""
        try:
            # Debug: Log the task details
            logger.info(f"Attempting to queue message automation for message {message_id}")
            logger.info(f"Celery broker URL: {celery_app.conf.broker_url}")
            logger.info(f"Celery result backend: {celery_app.conf.result_backend}")
            
            result = celery_app.send_task(
                'app.tasks.automation_tasks.process_message_automation',
                args=[message_id],
                queue='automation'
            )
            logger.info(f"Message automation queued for message {message_id} - Task ID: {result.id}")
            return True
        except Exception as e:
            logger.error(f"Error queuing message automation: {str(e)}")
            logger.exception("Full error traceback:")
            return False
    
    @staticmethod
    def queue_new_contact_automation(contact_id: int):
        """Queue new contact automation task for worker."""
        try:
            celery_app.send_task(
                'app.tasks.automation_tasks.process_new_contact_automation',
                args=[contact_id],
                queue='automation'
            )
            logger.info(f"New contact automation queued for contact {contact_id}")
            return True
        except Exception as e:
            logger.error(f"Error queuing new contact automation: {str(e)}")
            return False
    
    @staticmethod
    def queue_send_message(contact_id: int, message_content: str, user_id: int):
        """Queue send message task for worker."""
        try:
            celery_app.send_task(
                'app.tasks.message_tasks.send_whatsapp_message',
                args=[contact_id, message_content, user_id],
                queue='messages'
            )
            logger.info(f"Send message queued for contact {contact_id}")
            return True
        except Exception as e:
            logger.error(f"Error queuing send message: {str(e)}")
            return False
    
    @staticmethod
    def queue_automation_execution(automation_id: int, contact_id: int = None, user_id: int = None):
        """Queue automation execution task for worker."""
        try:
            celery_app.send_task(
                'app.tasks.automation_tasks.execute_automation_for_contact',
                args=[automation_id, contact_id],
                queue='automation'
            )
            logger.info(f"Automation execution queued for automation {automation_id}")
            return True
        except Exception as e:
            logger.error(f"Error queuing automation execution: {str(e)}")
            return False
    
    @staticmethod
    def queue_message_status_update(whatsapp_message_id: str, status: str, timestamp: int = None):
        """Queue message status update task for worker."""
        try:
            celery_app.send_task(
                'app.tasks.message_tasks.process_message_status_update',
                args=[whatsapp_message_id, status, timestamp],
                queue='messages'
            )
            logger.info(f"Message status update queued for {whatsapp_message_id}")
            return True
        except Exception as e:
            logger.error(f"Error queuing message status update: {str(e)}")
            return False
