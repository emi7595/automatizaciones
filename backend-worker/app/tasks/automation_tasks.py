"""
Automation background tasks for processing triggers and actions.
Uses backend API instead of duplicating business logic.
"""
from celery import current_task
from app.core.celery import celery_app
from app.core.api_client import get_automations_by_trigger, execute_automation_for_contact, record_automation_result
from app.core.logging import get_logger, log_performance
import asyncio

logger = get_logger(__name__)


@celery_app.task(bind=True)
def test_connection(self):
    """Test task to verify worker is receiving tasks."""
    logger.info("🧪 TEST TASK RECEIVED: Worker connection is working!")
    logger.info(f"🧪 Task ID: {self.request.id}")
    logger.info(f"🧪 Task queue: {self.request.delivery_info.get('routing_key', 'unknown')}")
    return {"status": "success", "message": "Worker is receiving tasks"}


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
def execute_automation_for_contact_task(self, automation_id: int, contact_id: int):
    """
    Execute a specific automation for a specific contact via backend API.
    """
    logger.info(f"Executing automation {automation_id} for contact {contact_id}")
    
    try:
        # Execute automation via backend API
        result = asyncio.run(execute_automation_for_contact(automation_id, contact_id))
        
        if result.get("success"):
            logger.info(f"Automation {automation_id} executed successfully for contact {contact_id}")
            return {"status": "completed", "result": result}
        else:
            logger.error(f"Automation {automation_id} execution failed: {result.get('error')}")
            return {"status": "failed", "error": result.get("error")}
        
    except Exception as e:
        logger.error(f"Error executing automation {automation_id} for contact {contact_id}: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
@log_performance()
def process_scheduled_automations(self):
    """
    Process scheduled automations that should run now via backend API.
    """
    logger.info("Processing scheduled automations")
    
    try:
        # Get scheduled automations from backend API
        automations = asyncio.run(get_automations_by_trigger("scheduled"))
        
        if not automations:
            logger.info("No scheduled automations found")
            return {"status": "completed", "automations_processed": 0}
        
        logger.info(f"Found {len(automations)} scheduled automations")
        
        # Execute each automation via backend API
        results = []
        successful = 0
        
        for automation in automations:
            try:
                result = asyncio.run(execute_automation_for_contact(
                    automation["id"],
                    contact_id=None,  # Backend will handle scheduled execution
                    user_id=None
                ))
                
                if result.get("success"):
                    successful += 1
                    logger.info(f"Scheduled automation {automation['id']} executed successfully")
                else:
                    logger.error(f"Scheduled automation {automation['id']} failed: {result.get('error')}")
                
                results.append({
                    "automation_id": automation["id"],
                    "success": result.get("success", False),
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error executing scheduled automation {automation['id']}: {str(e)}")
                results.append({
                    "automation_id": automation["id"],
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Scheduled automations processed: {successful}/{len(automations)} successful")
        return {
            "status": "completed",
            "automations_processed": len(automations),
            "successful": successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in scheduled automation processing: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
@log_performance()
def process_new_contact_automation(self, contact_id: int):
    """
    Process new contact automation for a specific contact via backend API.
    """
    logger.info(f"Processing new contact automation for contact {contact_id}")
    
    try:
        # Get new contact automations from backend API
        automations = asyncio.run(get_automations_by_trigger("new_contact"))
        
        if not automations:
            logger.info("No new contact automations found")
            return {"status": "completed", "automations_processed": 0}
        
        logger.info(f"Found {len(automations)} new contact automations")
        
        # Execute each automation for the contact via backend API
        results = []
        successful = 0
        
        for automation in automations:
            try:
                result = asyncio.run(execute_automation_for_contact(
                    automation["id"],
                    contact_id=contact_id,
                    user_id=None
                ))
                
                if result.get("success"):
                    successful += 1
                    logger.info(f"New contact automation {automation['id']} executed successfully for contact {contact_id}")
                else:
                    logger.error(f"New contact automation {automation['id']} failed: {result.get('error')}")
                
                results.append({
                    "automation_id": automation["id"],
                    "success": result.get("success", False),
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error executing new contact automation {automation['id']}: {str(e)}")
                results.append({
                    "automation_id": automation["id"],
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"New contact automations processed: {successful}/{len(automations)} successful")
        return {
            "status": "completed",
            "automations_processed": len(automations),
            "successful": successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in new contact automation processing: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
@log_performance()
def process_message_automation(self, message_id: int):
    """
    Process message-based automations for a specific message via backend API.
    """
    logger.info(f"🚀 TASK RECEIVED: Processing message automation for message {message_id}")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Task args: {self.request.args}")
    logger.info(f"Task kwargs: {self.request.kwargs}")
    
    try:
        # Get message-based automations from backend API
        message_automations = asyncio.run(get_automations_by_trigger("message_received"))
        keyword_automations = asyncio.run(get_automations_by_trigger("keyword"))
        
        all_automations = message_automations + keyword_automations
        
        if not all_automations:
            logger.info("No message-based automations found")
            return {"status": "completed", "automations_processed": 0}
        
        logger.info(f"Found {len(all_automations)} message-based automations")
        
        # Execute each automation via backend API
        results = []
        successful = 0
        
        for automation in all_automations:
            try:
                result = asyncio.run(execute_automation_for_contact(
                    automation["id"],
                    contact_id=None,  # Backend will handle message-based execution
                    user_id=None
                ))
                
                if result.get("success"):
                    successful += 1
                    logger.info(f"Message automation {automation['id']} executed successfully")
                else:
                    logger.error(f"Message automation {automation['id']} failed: {result.get('error')}")
                
                results.append({
                    "automation_id": automation["id"],
                    "trigger_type": automation.get("trigger_type", "unknown"),
                    "success": result.get("success", False),
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error executing message automation {automation['id']}: {str(e)}")
                results.append({
                    "automation_id": automation["id"],
                    "trigger_type": automation.get("trigger_type", "unknown"),
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Message automations processed: {successful}/{len(all_automations)} successful")
        return {
            "status": "completed",
            "automations_processed": len(all_automations),
            "successful": successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in message automation processing: {str(e)}")
        logger.exception("Full error traceback:")
        return {"status": "failed", "error": str(e)}
