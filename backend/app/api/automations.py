"""
Automation API endpoints for managing automation rules and execution.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.automation import (
    AutomationCreateRequest, AutomationUpdateRequest, AutomationRead,
    AutomationListResponse, AutomationExecutionRequest, AutomationExecutionResponse,
    AutomationStatsResponse, AutomationLogListResponse, AutomationSearchFilters
)
from app.services.automation_service import AutomationService
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)
router = APIRouter(prefix="/api/automations", tags=["automations"])


@router.post("/", response_model=AutomationRead)
@log_performance()
async def create_automation(
    request: AutomationCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new automation rule.
    """
    logger.info(f"API: Creating automation: {request.name}")
    logger.debug(f"Request: {request}")
    
    try:
        automation_service = AutomationService(db)
        result = automation_service.create_automation(request, user_id=1)  # TODO: Get from auth
        
        if not result["success"]:
            logger.error(f"API: Automation creation failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"API: Automation created successfully: {result['automation_id']}")
        return result["automation"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in create_automation: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=AutomationListResponse)
@log_performance()
async def get_automations(
    name: Optional[str] = Query(None, description="Filter by automation name"),
    trigger_type: Optional[str] = Query(None, description="Filter by trigger type"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    created_by: Optional[int] = Query(None, description="Filter by creator"),
    date_from: Optional[datetime] = Query(None, description="Filter by creation date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by creation date to"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get automations with optional filtering and pagination.
    """
    logger.info(f"API: Getting automations with filters")
    logger.debug(f"Filters: name={name}, trigger_type={trigger_type}, action_type={action_type}")
    
    try:
        filters = AutomationSearchFilters(
            name=name,
            trigger_type=trigger_type,
            action_type=action_type,
            is_active=is_active,
            created_by=created_by,
            date_from=date_from,
            date_to=date_to,
            page=page,
            size=size
        )
        
        automation_service = AutomationService(db)
        result = automation_service.get_automations(filters)
        
        if not result["success"]:
            logger.error(f"API: Get automations failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"API: Found {len(result['automations'])} automations")
        return AutomationListResponse(
            automations=result["automations"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in get_automations: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{automation_id}", response_model=AutomationRead)
@log_performance()
async def get_automation(
    automation_id: int = Path(..., description="Automation ID"),
    db: Session = Depends(get_db)
):
    """
    Get a specific automation by ID.
    """
    logger.info(f"API: Getting automation: {automation_id}")
    
    try:
        automation_service = AutomationService(db)
        result = automation_service.get_automation(automation_id)
        
        if not result["success"]:
            logger.error(f"API: Get automation failed: {result['error']}")
            raise HTTPException(status_code=404, detail=result["error"])
        
        logger.info(f"API: Found automation: {result['automation'].name}")
        return result["automation"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in get_automation: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{automation_id}", response_model=AutomationRead)
@log_performance()
async def update_automation(
    automation_id: int = Path(..., description="Automation ID"),
    request: AutomationUpdateRequest = None,
    db: Session = Depends(get_db)
):
    """
    Update an existing automation.
    """
    logger.info(f"API: Updating automation: {automation_id}")
    logger.debug(f"Request: {request}")
    
    try:
        automation_service = AutomationService(db)
        result = automation_service.update_automation(automation_id, request, user_id=1)  # TODO: Get from auth
        
        if not result["success"]:
            logger.error(f"API: Automation update failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"API: Automation updated successfully: {automation_id}")
        return result["automation"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in update_automation: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{automation_id}")
@log_performance()
async def delete_automation(
    automation_id: int = Path(..., description="Automation ID"),
    db: Session = Depends(get_db)
):
    """
    Delete an automation.
    """
    logger.info(f"API: Deleting automation: {automation_id}")
    
    try:
        automation_service = AutomationService(db)
        result = automation_service.delete_automation(automation_id)
        
        if not result["success"]:
            logger.error(f"API: Automation deletion failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"API: Automation deleted successfully: {automation_id}")
        return {"message": "Automation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in delete_automation: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{automation_id}/execute", response_model=AutomationExecutionResponse)
@log_performance()
async def execute_automation(
    automation_id: int = Path(..., description="Automation ID"),
    contact_id: Optional[int] = Query(None, description="Specific contact to target"),
    test_mode: bool = Query(False, description="Whether this is a test execution"),
    db: Session = Depends(get_db)
):
    """
    Execute an automation manually.
    """
    logger.info(f"API: Executing automation: {automation_id}")
    logger.debug(f"Parameters: contact_id={contact_id}, test_mode={test_mode}")
    
    try:
        request = AutomationExecutionRequest(
            automation_id=automation_id,
            contact_id=contact_id,
            test_mode=test_mode
        )
        
        automation_service = AutomationService(db)
        result = automation_service.execute_automation(request, user_id=1)  # TODO: Get from auth
        
        if not result["success"]:
            logger.error(f"API: Automation execution failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"API: Automation executed successfully: {automation_id}")
        return AutomationExecutionResponse(
            success=True,
            message=result.get("message", "Automation executed successfully"),
            contacts_affected=result.get("contacts_affected", 0),
            execution_time=result.get("execution_time", 0),
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in execute_automation: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview", response_model=AutomationStatsResponse)
@log_performance()
async def get_automation_stats(
    db: Session = Depends(get_db)
):
    """
    Get automation statistics and overview.
    """
    logger.info("API: Getting automation statistics")
    
    try:
        automation_service = AutomationService(db)
        result = automation_service.get_automation_stats()
        
        if not result["success"]:
            logger.error(f"API: Get automation stats failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info("API: Automation statistics retrieved successfully")
        return AutomationStatsResponse(**result["stats"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in get_automation_stats: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{automation_id}/logs", response_model=AutomationLogListResponse)
@log_performance()
async def get_automation_logs(
    automation_id: int = Path(..., description="Automation ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get execution logs for a specific automation.
    """
    logger.info(f"API: Getting logs for automation: {automation_id}")
    
    try:
        from app.models.automation_log import AutomationLog
        
        # Get logs with pagination
        query = db.query(AutomationLog).filter(AutomationLog.automation_id == automation_id)
        total = query.count()
        
        logs = query.order_by(desc(AutomationLog.executed_at))\
                   .offset((page - 1) * size)\
                   .limit(size)\
                   .all()
        
        logger.info(f"API: Found {len(logs)} logs for automation {automation_id}")
        return AutomationLogListResponse(
            logs=logs,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"API: Unexpected error in get_automation_logs: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples/triggers")
async def get_trigger_examples():
    """
    Get examples of trigger conditions for different trigger types.
    """
    logger.info("API: Getting trigger examples")
    
    examples = [
        {
            "trigger_type": "new_contact",
            "example_conditions": {
                "days": 1
            },
            "description": "Trigger when a new contact is created within the last N days"
        },
        {
            "trigger_type": "birthday",
            "example_conditions": {
                "date_range": "today",
                "timezone": "UTC"
            },
            "description": "Trigger on contact birthdays"
        },
        {
            "trigger_type": "message_received",
            "example_conditions": {
                "hours": 24,
                "keywords": ["help", "support"],
                "sender_criteria": {
                    "min_messages": 1
                }
            },
            "description": "Trigger when a message is received with specific keywords"
        },
        {
            "trigger_type": "keyword",
            "example_conditions": {
                "keywords": ["hello", "hi", "hey"],
                "case_sensitive": False
            },
            "description": "Trigger when specific keywords are detected in messages"
        },
        {
            "trigger_type": "scheduled",
            "example_conditions": {
                "schedule": {
                    "type": "daily",
                    "time": "09:00",
                    "timezone": "UTC"
                }
            },
            "description": "Trigger on a scheduled basis"
        },
        {
            "trigger_type": "time_based",
            "example_conditions": {
                "time_criteria": {
                    "days_of_week": [1, 2, 3, 4, 5],
                    "time_range": "09:00-17:00"
                }
            },
            "description": "Trigger based on time criteria"
        }
    ]
    
    return {"examples": examples}


@router.get("/examples/actions")
async def get_action_examples():
    """
    Get examples of action payloads for different action types.
    """
    logger.info("API: Getting action examples")
    
    examples = [
        {
            "action_type": "send_message",
            "example_payload": {
                "message": "Hello! Thank you for contacting us. We'll get back to you soon.",
                "message_type": "text"
            },
            "description": "Send a WhatsApp message to the contact"
        },
        {
            "action_type": "update_contact",
            "example_payload": {
                "update_fields": {
                    "tags": ["automated_response"],
                    "notes": "Received automated welcome message"
                }
            },
            "description": "Update contact information"
        },
        {
            "action_type": "log_activity",
            "example_payload": {
                "log_message": "Birthday automation triggered",
                "activity_type": "automation"
            },
            "description": "Log an activity for the contact"
        },
        {
            "action_type": "trigger_automation",
            "example_payload": {
                "target_automation_id": 2,
                "delay_seconds": 300
            },
            "description": "Trigger another automation"
        }
    ]
    
    return {"examples": examples}
