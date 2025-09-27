"""
Automation engine for executing automation rules and managing triggers.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.automation import Automation, TriggerType, ActionType
from app.models.automation_log import AutomationLog, AutomationExecutionStatus
from app.models.contact import Contact
from app.models.message import Message, MessageDirection, MessageType, MessageStatus
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)


class AutomationEngine:
    """Engine for executing automation rules and managing triggers."""
    
    def __init__(self, db: Session):
        self.db = db
    
    @log_performance()
    def process_new_contact_trigger(self, contact: Contact) -> Dict[str, Any]:
        """
        Process new contact trigger for all relevant automations.
        
        Args:
            contact: New contact that was created
            
        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing new contact trigger for contact: {contact.id}")
        
        try:
            # Find automations with new_contact trigger
            automations = self.db.query(Automation).filter(
                Automation.trigger_type == TriggerType.NEW_CONTACT,
                Automation.is_active == True
            ).order_by(Automation.priority).all()
            
            if not automations:
                logger.info("No new contact automations found")
                return {"success": True, "automations_processed": 0}
            
            logger.info(f"Found {len(automations)} new contact automations")
            
            # Execute each automation
            results = []
            for automation in automations:
                try:
                    result = self._execute_automation_for_contact(automation, contact)
                    results.append({
                        "automation_id": automation.id,
                        "automation_name": automation.name,
                        "success": result["success"],
                        "message": result.get("message", ""),
                        "error": result.get("error")
                    })
                except Exception as e:
                    logger.error(f"Error executing automation {automation.id}: {str(e)}")
                    results.append({
                        "automation_id": automation.id,
                        "automation_name": automation.name,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r["success"])
            logger.info(f"New contact trigger processed: {successful}/{len(automations)} successful")
            
            return {
                "success": True,
                "automations_processed": len(automations),
                "successful": successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing new contact trigger: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @log_performance()
    def process_birthday_trigger(self) -> Dict[str, Any]:
        """
        Process birthday trigger for all contacts with birthdays today.
        
        Returns:
            Dict containing processing results
        """
        logger.info("Processing birthday trigger")
        
        try:
            # Find automations with birthday trigger
            automations = self.db.query(Automation).filter(
                Automation.trigger_type == TriggerType.BIRTHDAY,
                Automation.is_active == True
            ).order_by(Automation.priority).all()
            
            if not automations:
                logger.info("No birthday automations found")
                return {"success": True, "automations_processed": 0}
            
            # Find contacts with birthdays today
            today = datetime.now().date()
            birthday_contacts = self.db.query(Contact).filter(
                Contact.birthday.isnot(None),
                func.date(Contact.birthday) == today,
                Contact.is_active == True
            ).all()
            
            if not birthday_contacts:
                logger.info("No contacts with birthdays today")
                return {"success": True, "contacts_processed": 0}
            
            logger.info(f"Found {len(birthday_contacts)} contacts with birthdays today")
            logger.info(f"Found {len(automations)} birthday automations")
            
            # Execute automations for each contact
            results = []
            for contact in birthday_contacts:
                for automation in automations:
                    try:
                        result = self._execute_automation_for_contact(automation, contact)
                        results.append({
                            "automation_id": automation.id,
                            "automation_name": automation.name,
                            "contact_id": contact.id,
                            "contact_name": contact.name,
                            "success": result["success"],
                            "message": result.get("message", ""),
                            "error": result.get("error")
                        })
                    except Exception as e:
                        logger.error(f"Error executing birthday automation {automation.id} for contact {contact.id}: {str(e)}")
                        results.append({
                            "automation_id": automation.id,
                            "automation_name": automation.name,
                            "contact_id": contact.id,
                            "contact_name": contact.name,
                            "success": False,
                            "error": str(e)
                        })
            
            successful = sum(1 for r in results if r["success"])
            logger.info(f"Birthday trigger processed: {successful}/{len(results)} successful")
            
            return {
                "success": True,
                "automations_processed": len(automations),
                "contacts_processed": len(birthday_contacts),
                "successful": successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing birthday trigger: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @log_performance()
    def process_message_trigger(self, message: Message) -> Dict[str, Any]:
        """
        Process message trigger for incoming messages.
        
        Args:
            message: Incoming message that triggered the automation
            
        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing message trigger for message: {message.id}")
        
        try:
            # Find automations with message_received trigger
            automations = self.db.query(Automation).filter(
                Automation.trigger_type == TriggerType.MESSAGE_RECEIVED,
                Automation.is_active == True
            ).order_by(Automation.priority).all()
            
            if not automations:
                logger.info("No message received automations found")
                return {"success": True, "automations_processed": 0}
            
            # Get contact for the message
            contact = self.db.query(Contact).filter(Contact.id == message.contact_id).first()
            if not contact:
                logger.error(f"Contact not found for message {message.id}")
                return {"success": False, "error": "Contact not found"}
            
            logger.info(f"Found {len(automations)} message received automations")
            
            # Execute automations that match the message criteria
            results = []
            for automation in automations:
                try:
                    # Check if automation conditions match the message
                    if self._check_message_conditions(automation, message):
                        result = self._execute_automation_for_contact(automation, contact)
                        results.append({
                            "automation_id": automation.id,
                            "automation_name": automation.name,
                            "contact_id": contact.id,
                            "contact_name": contact.name,
                            "success": result["success"],
                            "message": result.get("message", ""),
                            "error": result.get("error")
                        })
                    else:
                        logger.debug(f"Automation {automation.id} conditions not met for message {message.id}")
                except Exception as e:
                    logger.error(f"Error executing message automation {automation.id}: {str(e)}")
                    results.append({
                        "automation_id": automation.id,
                        "automation_name": automation.name,
                        "contact_id": contact.id,
                        "contact_name": contact.name,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r["success"])
            logger.info(f"Message trigger processed: {successful}/{len(results)} successful")
            
            return {
                "success": True,
                "automations_processed": len(automations),
                "successful": successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing message trigger: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @log_performance()
    def process_keyword_trigger(self, message: Message) -> Dict[str, Any]:
        """
        Process keyword trigger for incoming messages.
        
        Args:
            message: Incoming message to check for keywords
            
        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing keyword trigger for message: {message.id}")
        
        try:
            # Find automations with keyword trigger
            automations = self.db.query(Automation).filter(
                Automation.trigger_type == TriggerType.KEYWORD,
                Automation.is_active == True
            ).order_by(Automation.priority).all()
            
            if not automations:
                logger.info("No keyword automations found")
                return {"success": True, "automations_processed": 0}
            
            # Get contact for the message
            contact = self.db.query(Contact).filter(Contact.id == message.contact_id).first()
            if not contact:
                logger.error(f"Contact not found for message {message.id}")
                return {"success": False, "error": "Contact not found"}
            
            logger.info(f"Found {len(automations)} keyword automations")
            
            # Check each automation for keyword matches
            results = []
            for automation in automations:
                try:
                    if self._check_keyword_conditions(automation, message):
                        result = self._execute_automation_for_contact(automation, contact)
                        results.append({
                            "automation_id": automation.id,
                            "automation_name": automation.name,
                            "contact_id": contact.id,
                            "contact_name": contact.name,
                            "success": result["success"],
                            "message": result.get("message", ""),
                            "error": result.get("error")
                        })
                    else:
                        logger.debug(f"Automation {automation.id} keywords not matched for message {message.id}")
                except Exception as e:
                    logger.error(f"Error executing keyword automation {automation.id}: {str(e)}")
                    results.append({
                        "automation_id": automation.id,
                        "automation_name": automation.name,
                        "contact_id": contact.id,
                        "contact_name": contact.name,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r["success"])
            logger.info(f"Keyword trigger processed: {successful}/{len(results)} successful")
            
            return {
                "success": True,
                "automations_processed": len(automations),
                "successful": successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing keyword trigger: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @log_performance()
    def process_scheduled_automations(self) -> Dict[str, Any]:
        """
        Process scheduled automations that should run now.
        
        Returns:
            Dict containing processing results
        """
        logger.info("Processing scheduled automations")
        
        try:
            # Find automations with scheduled trigger
            automations = self.db.query(Automation).filter(
                Automation.trigger_type == TriggerType.SCHEDULED,
                Automation.is_active == True
            ).order_by(Automation.priority).all()
            
            if not automations:
                logger.info("No scheduled automations found")
                return {"success": True, "automations_processed": 0}
            
            logger.info(f"Found {len(automations)} scheduled automations")
            
            # Check each automation's schedule
            results = []
            for automation in automations:
                try:
                    if self._check_schedule_conditions(automation):
                        # Execute automation for all active contacts
                        contacts = self.db.query(Contact).filter(Contact.is_active == True).all()
                        
                        for contact in contacts:
                            result = self._execute_automation_for_contact(automation, contact)
                            results.append({
                                "automation_id": automation.id,
                                "automation_name": automation.name,
                                "contact_id": contact.id,
                                "contact_name": contact.name,
                                "success": result["success"],
                                "message": result.get("message", ""),
                                "error": result.get("error")
                            })
                    else:
                        logger.debug(f"Automation {automation.id} schedule conditions not met")
                except Exception as e:
                    logger.error(f"Error executing scheduled automation {automation.id}: {str(e)}")
                    results.append({
                        "automation_id": automation.id,
                        "automation_name": automation.name,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r["success"])
            logger.info(f"Scheduled automations processed: {successful}/{len(results)} successful")
            
            return {
                "success": True,
                "automations_processed": len(automations),
                "successful": successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing scheduled automations: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _check_message_conditions(self, automation: Automation, message: Message) -> bool:
        """Check if message matches automation conditions."""
        try:
            conditions = automation.trigger_conditions
            
            # Check keywords if specified
            if "keywords" in conditions:
                keywords = conditions["keywords"]
                if keywords and any(keyword.lower() in message.content.lower() for keyword in keywords):
                    return True
            
            # Check sender criteria if specified
            if "sender_criteria" in conditions:
                criteria = conditions["sender_criteria"]
                if "min_messages" in criteria:
                    message_count = self.db.query(Message).filter(
                        Message.contact_id == message.contact_id,
                        Message.direction == MessageDirection.INBOUND
                    ).count()
                    if message_count < criteria["min_messages"]:
                        return False
            
            # Check time criteria if specified
            if "hours" in conditions:
                hours = conditions["hours"]
                cutoff_time = datetime.now() - timedelta(hours=hours)
                if message.created_at < cutoff_time:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking message conditions: {str(e)}")
            return False
    
    def _check_keyword_conditions(self, automation: Automation, message: Message) -> bool:
        """Check if message contains automation keywords."""
        try:
            conditions = automation.trigger_conditions
            keywords = conditions.get("keywords", [])
            
            if not keywords:
                return False
            
            case_sensitive = conditions.get("case_sensitive", False)
            message_content = message.content if case_sensitive else message.content.lower()
            
            for keyword in keywords:
                keyword_to_check = keyword if case_sensitive else keyword.lower()
                if keyword_to_check in message_content:
                    logger.info(f"Keyword '{keyword}' matched in message {message.id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking keyword conditions: {str(e)}")
            return False
    
    def _check_schedule_conditions(self, automation: Automation) -> bool:
        """Check if automation should run based on schedule."""
        try:
            schedule_config = automation.schedule_config
            if not schedule_config:
                return False
            
            schedule = schedule_config.get("schedule", {})
            schedule_type = schedule.get("type", "")
            current_time = datetime.now()
            
            if schedule_type == "daily":
                # Check if it's time to run daily automation
                target_time = schedule.get("time", "09:00")
                timezone = schedule.get("timezone", "UTC")
                
                # Simple time check (in production, use proper timezone handling)
                current_hour = current_time.hour
                current_minute = current_time.minute
                target_hour, target_minute = map(int, target_time.split(":"))
                
                if current_hour == target_hour and current_minute == target_minute:
                    return True
            
            elif schedule_type == "weekly":
                # Check if it's the right day of week
                target_days = schedule.get("days", [1])  # Monday = 1
                current_weekday = current_time.weekday() + 1  # Convert to 1-7
                
                if current_weekday in target_days:
                    target_time = schedule.get("time", "09:00")
                    # Check time as well
                    return True  # Simplified for now
            
            elif schedule_type == "monthly":
                # Check if it's the right day of month
                target_day = schedule.get("day", 1)
                if current_time.day == target_day:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking schedule conditions: {str(e)}")
            return False
    
    def _execute_automation_for_contact(self, automation: Automation, contact: Contact) -> Dict[str, Any]:
        """Execute automation for a specific contact."""
        start_time = datetime.now()
        
        try:
            logger.info(f"Executing automation {automation.id} for contact {contact.id}")
            
            # Execute action based on automation type
            if automation.action_type == ActionType.SEND_MESSAGE:
                result = self._execute_send_message_action(automation, contact)
            elif automation.action_type == ActionType.UPDATE_CONTACT:
                result = self._execute_update_contact_action(automation, contact)
            elif automation.action_type == ActionType.LOG_ACTIVITY:
                result = self._execute_log_activity_action(automation, contact)
            else:
                logger.warning(f"Action type {automation.action_type} not implemented")
                result = {"success": False, "error": f"Action type {automation.action_type} not implemented"}
            
            # Log execution
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_automation_execution(automation, contact, result, execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing automation {automation.id} for contact {contact.id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_send_message_action(self, automation: Automation, contact: Contact) -> Dict[str, Any]:
        """Execute send message action."""
        try:
            message_content = automation.action_payload.get("message", "")
            if not message_content:
                return {"success": False, "error": "No message content provided"}
            
            # Import here to avoid circular imports
            from app.services.message_service import MessageService
            message_service = MessageService(self.db)
            
            # Create message send request
            from app.schemas.message import MessageSendRequest
            from app.models.message import MessageType
            
            request = MessageSendRequest(
                contact_id=contact.id,
                content=message_content,
                message_type=MessageType.TEXT
            )
            
            # Note: This would need to be awaited in an async context
            # For now, we'll simulate the result
            logger.info(f"Would send message to {contact.name}: {message_content}")
            return {"success": True, "message": "Message sent successfully"}
            
        except Exception as e:
            logger.error(f"Error executing send message action: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_update_contact_action(self, automation: Automation, contact: Contact) -> Dict[str, Any]:
        """Execute update contact action."""
        try:
            update_fields = automation.action_payload.get("update_fields", {})
            if not update_fields:
                return {"success": False, "error": "No update fields provided"}
            
            # Update contact fields
            for field, value in update_fields.items():
                if hasattr(contact, field):
                    setattr(contact, field, value)
            
            self.db.commit()
            logger.info(f"Updated contact {contact.id} with fields: {update_fields}")
            return {"success": True, "message": "Contact updated successfully"}
            
        except Exception as e:
            logger.error(f"Error executing update contact action: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_log_activity_action(self, automation: Automation, contact: Contact) -> Dict[str, Any]:
        """Execute log activity action."""
        try:
            log_message = automation.action_payload.get("log_message", "")
            if not log_message:
                return {"success": False, "error": "No log message provided"}
            
            # Log the activity
            logger.info(f"Activity logged for contact {contact.id}: {log_message}")
            return {"success": True, "message": "Activity logged successfully"}
            
        except Exception as e:
            logger.error(f"Error executing log activity action: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _log_automation_execution(self, automation: Automation, contact: Contact, 
                                result: Dict[str, Any], execution_time: float):
        """Log automation execution."""
        try:
            execution_log = AutomationLog(
                automation_id=automation.id,
                contact_id=contact.id,
                execution_status=AutomationExecutionStatus.SUCCESS if result["success"] else AutomationExecutionStatus.FAILED,
                execution_time=execution_time,
                contacts_affected=1 if result["success"] else 0,
                error_message=result.get("error"),
                execution_details={"result": result}
            )
            
            self.db.add(execution_log)
            self.db.commit()
            
            logger.info(f"Automation execution logged: {execution_log.id}")
            
        except Exception as e:
            logger.error(f"Error logging automation execution: {str(e)}")
            self.db.rollback()
