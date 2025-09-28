"""
Automation service for managing automation rules and execution.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.automation import Automation, TriggerType, ActionType
from app.models.automation_log import AutomationLog, ExecutionStatus
from app.models.contact import Contact
from app.models.message import Message, MessageDirection, MessageType, MessageStatus
from app.schemas.automation import (
    AutomationCreateRequest, AutomationUpdateRequest, AutomationSearchFilters,
    AutomationExecutionRequest, AutomationExecutionResponse
)
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)


class AutomationService:
    """Service for managing automations and their execution."""
    
    def __init__(self, db: Session):
        self.db = db
    
    @log_performance()
    def create_automation(self, request: AutomationCreateRequest, user_id: int) -> Dict[str, Any]:
        """
        Create a new automation rule.
        
        Args:
            request: Automation creation request
            user_id: ID of the user creating the automation
            
        Returns:
            Dict containing creation result and automation data
        """
        logger.info(f"Creating automation: {request.name}")
        logger.debug(f"Request details: {request}")
        
        try:
            # Validate trigger conditions
            validation_result = self._validate_trigger_conditions(
                request.trigger_type, request.trigger_conditions
            )
            if not validation_result["valid"]:
                logger.error(f"Invalid trigger conditions: {validation_result['error']}")
                return {"success": False, "error": validation_result["error"]}
            
            # Validate action payload
            validation_result = self._validate_action_payload(
                request.action_type, request.action_payload
            )
            if not validation_result["valid"]:
                logger.error(f"Invalid action payload: {validation_result['error']}")
                return {"success": False, "error": validation_result["error"]}
            
            # Create automation
            automation = Automation(
                name=request.name,
                description=request.description,
                trigger_type=request.trigger_type,
                trigger_conditions=request.trigger_conditions,
                action_type=request.action_type,
                action_payload=request.action_payload,
                schedule_config=request.schedule_config,
                is_active=request.is_active,
                priority=request.priority,
                created_by=user_id
            )
            
            self.db.add(automation)
            self.db.commit()
            self.db.refresh(automation)
            
            logger.info(f"Automation created successfully: {automation.id}")
            return {
                "success": True,
                "automation_id": automation.id,
                "automation": automation
            }
            
        except Exception as e:
            logger.error(f"Error creating automation: {str(e)}")
            logger.exception("Full error traceback:")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    @log_performance()
    def update_automation(self, automation_id: int, request: AutomationUpdateRequest, user_id: int) -> Dict[str, Any]:
        """
        Update an existing automation.
        
        Args:
            automation_id: ID of automation to update
            request: Update request
            user_id: ID of the user updating the automation
            
        Returns:
            Dict containing update result
        """
        logger.info(f"Updating automation: {automation_id}")
        logger.debug(f"Update request: {request}")
        
        try:
            automation = self.db.query(Automation).filter(Automation.id == automation_id).first()
            if not automation:
                logger.error(f"Automation {automation_id} not found")
                return {"success": False, "error": "Automation not found"}
            
            # Update fields if provided
            if request.name is not None:
                automation.name = request.name
            if request.description is not None:
                automation.description = request.description
            if request.trigger_conditions is not None:
                # Validate trigger conditions
                validation_result = self._validate_trigger_conditions(
                    automation.trigger_type, request.trigger_conditions
                )
                if not validation_result["valid"]:
                    logger.error(f"Invalid trigger conditions: {validation_result['error']}")
                    return {"success": False, "error": validation_result["error"]}
                automation.trigger_conditions = request.trigger_conditions
            if request.action_payload is not None:
                # Validate action payload
                validation_result = self._validate_action_payload(
                    automation.action_type, request.action_payload
                )
                if not validation_result["valid"]:
                    logger.error(f"Invalid action payload: {validation_result['error']}")
                    return {"success": False, "error": validation_result["error"]}
                automation.action_payload = request.action_payload
            if request.schedule_config is not None:
                automation.schedule_config = request.schedule_config
            if request.is_active is not None:
                automation.is_active = request.is_active
            if request.priority is not None:
                automation.priority = request.priority
            
            automation.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(automation)
            
            logger.info(f"Automation updated successfully: {automation.id}")
            return {
                "success": True,
                "automation": automation
            }
            
        except Exception as e:
            logger.error(f"Error updating automation: {str(e)}")
            logger.exception("Full error traceback:")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_automations(self, filters: AutomationSearchFilters) -> Dict[str, Any]:
        """
        Get automations with optional filtering and pagination.
        
        Args:
            filters: Search filters and pagination
            
        Returns:
            Dict containing automations and pagination info
        """
        logger.info(f"Getting automations with filters: {filters}")
        
        try:
            query = self.db.query(Automation)
            
            # Apply filters
            if filters.name:
                query = query.filter(Automation.name.ilike(f"%{filters.name}%"))
            if filters.trigger_type:
                query = query.filter(Automation.trigger_type == filters.trigger_type)
            if filters.action_type:
                query = query.filter(Automation.action_type == filters.action_type)
            if filters.is_active is not None:
                query = query.filter(Automation.is_active == filters.is_active)
            if filters.created_by:
                query = query.filter(Automation.created_by == filters.created_by)
            if filters.date_from:
                query = query.filter(Automation.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(Automation.created_at <= filters.date_to)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            automations = query.order_by(desc(Automation.priority), desc(Automation.created_at))\
                              .offset((filters.page - 1) * filters.size)\
                              .limit(filters.size)\
                              .all()
            
            logger.info(f"Found {len(automations)} automations out of {total} total")
            return {
                "success": True,
                "automations": automations,
                "total": total,
                "page": filters.page,
                "size": filters.size
            }
            
        except Exception as e:
            logger.error(f"Error getting automations: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_automation(self, automation_id: int) -> Dict[str, Any]:
        """
        Get a specific automation by ID.
        
        Args:
            automation_id: ID of automation to get
            
        Returns:
            Dict containing automation data
        """
        logger.info(f"Getting automation: {automation_id}")
        
        try:
            automation = self.db.query(Automation).filter(Automation.id == automation_id).first()
            if not automation:
                logger.error(f"Automation {automation_id} not found")
                return {"success": False, "error": "Automation not found"}
            
            logger.info(f"Found automation: {automation.name}")
            return {
                "success": True,
                "automation": automation
            }
            
        except Exception as e:
            logger.error(f"Error getting automation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_automation(self, automation_id: int) -> Dict[str, Any]:
        """
        Delete an automation.
        
        Args:
            automation_id: ID of automation to delete
            
        Returns:
            Dict containing deletion result
        """
        logger.info(f"Deleting automation: {automation_id}")
        
        try:
            automation = self.db.query(Automation).filter(Automation.id == automation_id).first()
            if not automation:
                logger.error(f"Automation {automation_id} not found")
                return {"success": False, "error": "Automation not found"}
            
            # Check if automation has execution logs
            log_count = self.db.query(AutomationLog).filter(
                AutomationLog.automation_id == automation_id
            ).count()
            
            if log_count > 0:
                logger.warning(f"Automation {automation_id} has {log_count} execution logs")
            
            self.db.delete(automation)
            self.db.commit()
            
            logger.info(f"Automation deleted successfully: {automation_id}")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error deleting automation: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    @log_performance()
    async def execute_automation(self, request: AutomationExecutionRequest, user_id: int) -> Dict[str, Any]:
        """
        Execute an automation manually.
        
        Args:
            request: Execution request
            user_id: ID of the user executing the automation
            
        Returns:
            Dict containing execution result
        """
        logger.info(f"Executing automation: {request.automation_id}")
        logger.debug(f"Execution request: {request}")
        
        try:
            # Get automation
            automation = self.db.query(Automation).filter(
                Automation.id == request.automation_id
            ).first()
            
            if not automation:
                logger.error(f"Automation {request.automation_id} not found")
                return {"success": False, "error": "Automation not found"}
            
            if not automation.is_active:
                logger.error(f"Automation {request.automation_id} is not active")
                return {"success": False, "error": "Automation is not active"}
            
            # Execute automation
            execution_result = await self._execute_automation_logic(
                automation, request.contact_id, request.test_mode, user_id
            )
            
            logger.info(f"Automation execution completed: {execution_result}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing automation: {str(e)}")
            logger.exception("Full error traceback:")
            return {"success": False, "error": str(e)}
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """
        Get automation statistics.
        
        Returns:
            Dict containing automation statistics
        """
        logger.info("Getting automation statistics")
        
        try:
            # Total automations
            total_automations = self.db.query(Automation).count()
            active_automations = self.db.query(Automation).filter(
                Automation.is_active == True
            ).count()
            inactive_automations = total_automations - active_automations
            
            # Execution stats
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            executions_today = self.db.query(AutomationLog).filter(
                func.date(AutomationLog.executed_at) == today
            ).count()
            
            executions_this_week = self.db.query(AutomationLog).filter(
                func.date(AutomationLog.executed_at) >= week_ago
            ).count()
            
            executions_this_month = self.db.query(AutomationLog).filter(
                func.date(AutomationLog.executed_at) >= month_ago
            ).count()
            
            # Success rate
            total_executions = self.db.query(AutomationLog).count()
            successful_executions = self.db.query(AutomationLog).filter(
                AutomationLog.execution_status == ExecutionStatus.SUCCESS
            ).count()
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Average execution time
            avg_execution_time = self.db.query(func.avg(AutomationLog.execution_time)).scalar() or 0
            
            stats = {
                "total_automations": total_automations,
                "active_automations": active_automations,
                "inactive_automations": inactive_automations,
                "executions_today": executions_today,
                "executions_this_week": executions_this_week,
                "executions_this_month": executions_this_month,
                "success_rate": round(success_rate, 2),
                "average_execution_time": round(avg_execution_time, 3)
            }
            
            logger.info(f"Automation statistics: {stats}")
            return {"success": True, "stats": stats}
            
        except Exception as e:
            logger.error(f"Error getting automation statistics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _validate_trigger_conditions(self, trigger_type: TriggerType, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trigger conditions based on trigger type."""
        try:
            if trigger_type == TriggerType.NEW_CONTACT:
                # No specific conditions required
                return {"valid": True}
            
            elif trigger_type == TriggerType.BIRTHDAY:
                # Should have date range or specific date
                if "date_range" not in conditions and "specific_date" not in conditions:
                    return {"valid": False, "error": "Birthday trigger requires date_range or specific_date"}
                return {"valid": True}
            
            elif trigger_type == TriggerType.MESSAGE_RECEIVED:
                # Should have message criteria
                if "keywords" not in conditions and "sender_criteria" not in conditions:
                    return {"valid": False, "error": "Message trigger requires keywords or sender_criteria"}
                return {"valid": True}
            
            elif trigger_type == TriggerType.KEYWORD:
                # Should have keywords
                if "keywords" not in conditions or not conditions["keywords"]:
                    return {"valid": False, "error": "Keyword trigger requires keywords list"}
                return {"valid": True}
            
            elif trigger_type == TriggerType.SCHEDULED:
                # Should have schedule configuration
                if "schedule" not in conditions:
                    return {"valid": False, "error": "Scheduled trigger requires schedule configuration"}
                return {"valid": True}
            
            elif trigger_type == TriggerType.TIME_BASED:
                # Should have time criteria
                if "time_criteria" not in conditions:
                    return {"valid": False, "error": "Time-based trigger requires time_criteria"}
                return {"valid": True}
            
            elif trigger_type == TriggerType.MANUAL:
                # No specific conditions required
                return {"valid": True}
            
            else:
                return {"valid": False, "error": f"Unknown trigger type: {trigger_type}"}
                
        except Exception as e:
            logger.error(f"Error validating trigger conditions: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    def _validate_action_payload(self, action_type: ActionType, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate action payload based on action type."""
        try:
            if action_type == ActionType.SEND_MESSAGE:
                # Should have message content
                if "message" not in payload or not payload["message"]:
                    return {"valid": False, "error": "Send message action requires message content"}
                return {"valid": True}
            
            elif action_type == ActionType.ADD_TO_GROUP:
                # Should have group information
                if "group_id" not in payload:
                    return {"valid": False, "error": "Add to group action requires group_id"}
                return {"valid": True}
            
            elif action_type == ActionType.UPDATE_CONTACT:
                # Should have update fields
                if "update_fields" not in payload or not payload["update_fields"]:
                    return {"valid": False, "error": "Update contact action requires update_fields"}
                return {"valid": True}
            
            elif action_type == ActionType.TRIGGER_AUTOMATION:
                # Should have target automation
                if "target_automation_id" not in payload:
                    return {"valid": False, "error": "Trigger automation action requires target_automation_id"}
                return {"valid": True}
            
            elif action_type == ActionType.SEND_EMAIL:
                # Should have email details
                if "email_template" not in payload and "email_content" not in payload:
                    return {"valid": False, "error": "Send email action requires email_template or email_content"}
                return {"valid": True}
            
            elif action_type == ActionType.LOG_ACTIVITY:
                # Should have log message
                if "log_message" not in payload:
                    return {"valid": False, "error": "Log activity action requires log_message"}
                return {"valid": True}
            
            else:
                return {"valid": False, "error": f"Unknown action type: {action_type}"}
                
        except Exception as e:
            logger.error(f"Error validating action payload: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    async def _execute_automation_logic(self, automation: Automation, contact_id: Optional[int], 
                                 test_mode: bool, user_id: int) -> Dict[str, Any]:
        """Execute the automation logic."""
        start_time = datetime.now()
        
        try:
            # Find contacts to process
            contacts = self._find_contacts_for_automation(automation, contact_id)
            
            if not contacts:
                logger.info(f"No contacts found for automation {automation.id}")
                return {
                    "success": True,
                    "message": "No contacts found for automation",
                    "contacts_affected": 0,
                    "execution_time": 0
                }
            
            # Execute action for each contact
            contacts_affected = 0
            errors = []
            
            for contact in contacts:
                try:
                    action_result = await self._execute_action(automation, contact, test_mode, user_id)
                    if action_result["success"]:
                        contacts_affected += 1
                    else:
                        errors.append(f"Contact {contact.id}: {action_result['error']}")
                except Exception as e:
                    error_msg = f"Contact {contact.id}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Log execution
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if not test_mode:
                self._log_automation_execution(
                    automation, contacts_affected, execution_time, errors, user_id
                )
            
            return {
                "success": True,
                "message": f"Automation executed successfully",
                "contacts_affected": contacts_affected,
                "execution_time": execution_time,
                "errors": errors if errors else None
            }
            
        except Exception as e:
            logger.error(f"Error in automation execution logic: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contacts_affected": 0,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    def _find_contacts_for_automation(self, automation: Automation, contact_id: Optional[int]) -> List[Contact]:
        """Find contacts that match the automation trigger conditions."""
        try:
            if contact_id:
                # Specific contact requested
                contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
                return [contact] if contact else []
            
            # Find contacts based on trigger type
            if automation.trigger_type == TriggerType.NEW_CONTACT:
                # Get recently created contacts
                days = automation.trigger_conditions.get("days", 1)
                cutoff_date = datetime.now() - timedelta(days=days)
                return self.db.query(Contact).filter(
                    Contact.created_at >= cutoff_date,
                    Contact.is_active == True
                ).all()
            
            elif automation.trigger_type == TriggerType.BIRTHDAY:
                # Get contacts with birthdays today
                today = datetime.now().date()
                return self.db.query(Contact).filter(
                    Contact.birthday.isnot(None),
                    func.date(Contact.birthday) == today,
                    Contact.is_active == True
                ).all()
            
            elif automation.trigger_type == TriggerType.MESSAGE_RECEIVED:
                # Get contacts who sent messages recently
                hours = automation.trigger_conditions.get("hours", 24)
                cutoff_time = datetime.now() - timedelta(hours=hours)
                return self.db.query(Contact).join(Message).filter(
                    Message.direction == MessageDirection.INBOUND,
                    Message.created_at >= cutoff_time,
                    Contact.is_active == True
                ).distinct().all()
            
            elif automation.trigger_type == TriggerType.KEYWORD:
                # Get contacts who sent messages with specific keywords
                keywords = automation.trigger_conditions.get("keywords", [])
                if not keywords:
                    return []
                
                keyword_filter = or_(*[Message.content.ilike(f"%{keyword}%") for keyword in keywords])
                return self.db.query(Contact).join(Message).filter(
                    Message.direction == MessageDirection.INBOUND,
                    keyword_filter,
                    Contact.is_active == True
                ).distinct().all()
            
            elif automation.trigger_type == TriggerType.TIME_BASED:
                # Get all active contacts for time-based triggers
                return self.db.query(Contact).filter(Contact.is_active == True).all()
            
            elif automation.trigger_type == TriggerType.MANUAL:
                # Get all active contacts for manual triggers
                return self.db.query(Contact).filter(Contact.is_active == True).all()
            
            else:
                logger.warning(f"Unknown trigger type: {automation.trigger_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error finding contacts for automation: {str(e)}")
            return []
    
    async def _execute_action(self, automation: Automation, contact: Contact, test_mode: bool, user_id: int) -> Dict[str, Any]:
        """Execute the automation action for a specific contact."""
        try:
            if automation.action_type == ActionType.SEND_MESSAGE:
                return await self._execute_send_message_action(automation, contact, test_mode, user_id)
            
            elif automation.action_type == ActionType.UPDATE_CONTACT:
                return self._execute_update_contact_action(automation, contact, test_mode, user_id)
            
            elif automation.action_type == ActionType.LOG_ACTIVITY:
                return self._execute_log_activity_action(automation, contact, test_mode, user_id)
            
            else:
                logger.warning(f"Action type {automation.action_type} not implemented yet")
                return {"success": False, "error": f"Action type {automation.action_type} not implemented"}
                
        except Exception as e:
            logger.error(f"Error executing action for contact {contact.id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_send_message_action(self, automation: Automation, contact: Contact, test_mode: bool, user_id: int) -> Dict[str, Any]:
        """Execute send message action."""
        try:
            message_content = automation.action_payload.get("message", "")
            if not message_content:
                return {"success": False, "error": "No message content provided"}
            
            if test_mode:
                logger.info(f"TEST MODE: Would send message to {contact.name}: {message_content}")
                return {"success": True, "message": "Test mode - message not sent"}
            
            # Queue message sending task for worker
            from app.core.task_queue import TaskQueue
            TaskQueue.queue_send_message(contact.id, message_content, user_id)
            return {"success": True, "message": "Message queued for sending"}
            
        except Exception as e:
            logger.error(f"Error executing send message action: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_update_contact_action(self, automation: Automation, contact: Contact, test_mode: bool, user_id: int) -> Dict[str, Any]:
        """Execute update contact action."""
        try:
            update_fields = automation.action_payload.get("update_fields", {})
            if not update_fields:
                return {"success": False, "error": "No update fields provided"}
            
            if test_mode:
                logger.info(f"TEST MODE: Would update contact {contact.name} with fields: {update_fields}")
                return {"success": True, "message": "Test mode - contact not updated"}
            
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
    
    def _execute_log_activity_action(self, automation: Automation, contact: Contact, test_mode: bool, user_id: int) -> Dict[str, Any]:
        """Execute log activity action."""
        try:
            log_message = automation.action_payload.get("log_message", "")
            if not log_message:
                return {"success": False, "error": "No log message provided"}
            
            if test_mode:
                logger.info(f"TEST MODE: Would log activity for {contact.name}: {log_message}")
                return {"success": True, "message": "Test mode - activity not logged"}
            
            # Log the activity (could be stored in a separate activity log table)
            logger.info(f"Activity logged for contact {contact.id}: {log_message}")
            return {"success": True, "message": "Activity logged successfully"}
            
        except Exception as e:
            logger.error(f"Error executing log activity action: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _log_automation_execution(self, automation: Automation, contacts_affected: int, 
                                execution_time: float, errors: List[str], user_id: int):
        """Log automation execution."""
        try:
            execution_log = AutomationLog(
                automation_id=automation.id,
                execution_status=ExecutionStatus.SUCCESS if not errors else ExecutionStatus.PARTIAL,
                execution_time=execution_time,
                contacts_affected=contacts_affected,
                error_message="; ".join(errors) if errors else None,
                execution_details={"errors": errors} if errors else None,
                executed_by=user_id
            )
            
            self.db.add(execution_log)
            self.db.commit()
            
            logger.info(f"Automation execution logged: {execution_log.id}")
            
        except Exception as e:
            logger.error(f"Error logging automation execution: {str(e)}")
            self.db.rollback()
