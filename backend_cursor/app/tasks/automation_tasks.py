"""
Automation background tasks for processing triggers and actions.
"""
from celery import current_task
from app.core.celery import celery_app
from app.database import SessionLocal
from app.models.automation import Automation
from app.models.contact import Contact
from app.models.automation_log import AutomationLog, ExecutionStatus
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def check_birthday_automations(self):
    """
    Check for contacts with birthdays today and trigger birthday automations.
    """
    db = SessionLocal()
    try:
        today = date.today()
        
        # Find contacts with birthdays today
        contacts_with_birthday = db.query(Contact).filter(
            Contact.is_active == True,
            Contact.birthday.isnot(None)
        ).all()
        
        birthday_contacts = []
        for contact in contacts_with_birthday:
            # Handle both known and unknown year birthdays
            if contact.birthday.year == 9999:
                # Unknown year - check if month and day match
                if contact.birthday.month == today.month and contact.birthday.day == today.day:
                    birthday_contacts.append(contact)
            else:
                # Known year - check exact date
                if contact.birthday.month == today.month and contact.birthday.day == today.day:
                    birthday_contacts.append(contact)
        
        # Find birthday automations
        birthday_automations = db.query(Automation).filter(
            Automation.trigger_type == "birthday",
            Automation.is_active == True
        ).order_by(Automation.priority.desc()).all()
        
        total_executed = 0
        total_failed = 0
        
        for automation in birthday_automations:
            for contact in birthday_contacts:
                try:
                    # Execute birthday automation for this contact
                    result = execute_automation_for_contact(automation, contact, db)
                    if result:
                        total_executed += 1
                    else:
                        total_failed += 1
                except Exception as e:
                    logger.error(f"Error executing birthday automation {automation.id} for contact {contact.id}: {e}")
                    total_failed += 1
        
        # Log execution
        log_automation_execution(
            automation_id=None,  # General birthday check
            contact_id=None,
            status=ExecutionStatus.SUCCESS if total_failed == 0 else ExecutionStatus.PARTIAL,
            contacts_affected=total_executed,
            execution_details={
                "total_contacts": len(birthday_contacts),
                "total_executed": total_executed,
                "total_failed": total_failed
            },
            db=db
        )
        
        return {
            "status": "completed",
            "contacts_processed": len(birthday_contacts),
            "automations_executed": total_executed,
            "failures": total_failed
        }
        
    except Exception as e:
        logger.error(f"Error in birthday automation check: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def execute_automation_for_contact(self, automation_id: int, contact_id: int):
    """
    Execute a specific automation for a specific contact.
    """
    db = SessionLocal()
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        
        if not automation or not contact:
            return {"status": "failed", "error": "Automation or contact not found"}
        
        if not automation.is_active:
            return {"status": "skipped", "error": "Automation is not active"}
        
        result = execute_automation_for_contact(automation, contact, db)
        
        return {"status": "completed", "result": result}
        
    except Exception as e:
        logger.error(f"Error executing automation {automation_id} for contact {contact_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


def execute_automation_for_contact(automation: Automation, contact: Contact, db) -> bool:
    """
    Execute automation logic for a contact.
    This is a placeholder for the actual automation execution logic.
    """
    try:
        # TODO: Implement actual automation execution based on action_type
        # This will be expanded in Phase 3 when we implement the automation engine
        
        action_type = automation.action_type
        action_payload = automation.get_action_payload()
        
        if action_type == "send_message":
            # TODO: Implement WhatsApp message sending
            logger.info(f"Would send message to {contact.name} with payload: {action_payload}")
            return True
        elif action_type == "update_contact":
            # TODO: Implement contact updates
            logger.info(f"Would update contact {contact.name} with payload: {action_payload}")
            return True
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error executing automation: {str(e)}")
        return False


def log_automation_execution(automation_id: int, contact_id: int, status: ExecutionStatus, 
                            contacts_affected: int, execution_details: dict, db):
    """
    Log automation execution details.
    """
    try:
        log_entry = AutomationLog(
            automation_id=automation_id,
            contact_id=contact_id,
            execution_status=status,
            contacts_affected=contacts_affected,
            execution_details=execution_details,
            executed_by="system"
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Error logging automation execution: {str(e)}")
        db.rollback()
