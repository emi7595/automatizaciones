"""
Automation background tasks for processing triggers and actions.
Uses backend API instead of duplicating business logic.
"""
from celery import current_task
from app.core.celery import celery_app
from app.core.api_client import get_automations_by_trigger, execute_automation_for_contact, record_automation_result
from app.core.logging import get_logger, log_performance
from app.database import SessionLocal
from app.models.automation import Automation
from app.models.contact import Contact
from app.services.automation_engine import AutomationEngine
import asyncio

logger = get_logger(__name__)


@celery_app.task(bind=True)
@log_performance()
def check_birthday_automations(self):
    """
    Check for contacts with birthdays today and trigger birthday automations.
    Uses backend API to get automations and execute them.
    """
    logger.info("Processing birthday automations")
    
    try:
        # Get birthday automations from backend API
        automations = asyncio.run(get_automations_by_trigger("birthday"))
        
        if not automations:
            logger.info("No birthday automations found")
            return {"status": "completed", "automations_processed": 0}
        
        logger.info(f"Found {len(automations)} birthday automations")
        
        # Execute each automation via backend API
        results = []
        successful = 0
        
        for automation in automations:
            try:
                # Execute automation via backend API
                result = asyncio.run(execute_automation_for_contact(
                    automation["id"],
                    contact_id=None,  # Backend will find contacts with birthdays
                    user_id=None
                ))
                
                if result.get("success"):
                    successful += 1
                    logger.info(f"Birthday automation {automation['id']} executed successfully")
                else:
                    logger.error(f"Birthday automation {automation['id']} failed: {result.get('error')}")
                
                results.append({
                    "automation_id": automation["id"],
                    "success": result.get("success", False),
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error executing birthday automation {automation['id']}: {str(e)}")
                results.append({
                    "automation_id": automation["id"],
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Birthday automations processed: {successful}/{len(automations)} successful")
        return {
            "status": "completed",
            "automations_processed": len(automations),
            "successful": successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in birthday automation check: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
@log_performance()
def execute_automation_for_contact(self, automation_id: int, contact_id: int):
    """
    Execute a specific automation for a specific contact.
    """
    logger.info(f"Executing automation {automation_id} for contact {contact_id}")
    db = SessionLocal()
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        
        if not automation or not contact:
            logger.error(f"Automation {automation_id} or contact {contact_id} not found")
            return {"status": "failed", "error": "Automation or contact not found"}
        
        if not automation.is_active:
            logger.warning(f"Automation {automation_id} is not active")
            return {"status": "skipped", "error": "Automation is not active"}
        
        automation_engine = AutomationEngine(db)
        result = automation_engine._execute_automation_for_contact(automation, contact)
        
        if result["success"]:
            logger.info(f"Automation {automation_id} executed successfully for contact {contact_id}")
        else:
            logger.error(f"Automation {automation_id} execution failed: {result.get('error')}")
        
        return {"status": "completed", "result": result}
        
    except Exception as e:
        logger.error(f"Error executing automation {automation_id} for contact {contact_id}: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
@log_performance()
def process_scheduled_automations(self):
    """
    Process scheduled automations that should run now.
    """
    logger.info("Processing scheduled automations")
    db = SessionLocal()
    try:
        automation_engine = AutomationEngine(db)
        result = automation_engine.process_scheduled_automations()
        
        if result["success"]:
            logger.info(f"Scheduled automations processed: {result['successful']}/{result['automations_processed']} successful")
            return {
                "status": "completed",
                "automations_processed": result["automations_processed"],
                "successful": result["successful"],
                "results": result.get("results", [])
            }
        else:
            logger.error(f"Scheduled automation processing failed: {result['error']}")
            return {"status": "failed", "error": result["error"]}
        
    except Exception as e:
        logger.error(f"Error in scheduled automation processing: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
@log_performance()
def process_new_contact_automation(self, contact_id: int):
    """
    Process new contact automation for a specific contact.
    """
    logger.info(f"Processing new contact automation for contact {contact_id}")
    db = SessionLocal()
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            logger.error(f"Contact {contact_id} not found")
            return {"status": "failed", "error": "Contact not found"}
        
        automation_engine = AutomationEngine(db)
        result = automation_engine.process_new_contact_trigger(contact)
        
        if result["success"]:
            logger.info(f"New contact automation processed: {result['successful']}/{result['automations_processed']} successful")
            return {
                "status": "completed",
                "automations_processed": result["automations_processed"],
                "successful": result["successful"],
                "results": result.get("results", [])
            }
        else:
            logger.error(f"New contact automation processing failed: {result['error']}")
            return {"status": "failed", "error": result["error"]}
        
    except Exception as e:
        logger.error(f"Error in new contact automation processing: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
@log_performance()
def process_message_automation(self, message_id: int):
    """
    Process message-based automations for a specific message.
    """
    logger.info(f"Processing message automation for message {message_id}")
    db = SessionLocal()
    try:
        from app.models.message import Message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            logger.error(f"Message {message_id} not found")
            return {"status": "failed", "error": "Message not found"}
        
        automation_engine = AutomationEngine(db)
        
        # Process both message_received and keyword triggers
        message_result = automation_engine.process_message_trigger(message)
        keyword_result = automation_engine.process_keyword_trigger(message)
        
        total_automations = message_result.get("automations_processed", 0) + keyword_result.get("automations_processed", 0)
        total_successful = message_result.get("successful", 0) + keyword_result.get("successful", 0)
        
        logger.info(f"Message automation processed: {total_successful}/{total_automations} successful")
        return {
            "status": "completed",
            "automations_processed": total_automations,
            "successful": total_successful,
            "message_results": message_result.get("results", []),
            "keyword_results": keyword_result.get("results", [])
        }
        
    except Exception as e:
        logger.error(f"Error in message automation processing: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
