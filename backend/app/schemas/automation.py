"""
Pydantic schemas for automation-related API operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.automation import TriggerType, ActionType


class AutomationCreateRequest(BaseModel):
    """Schema for creating a new automation."""
    name: str = Field(..., min_length=1, max_length=255, description="Automation name")
    description: Optional[str] = Field(None, max_length=1000, description="Automation description")
    trigger_type: TriggerType = Field(..., description="Type of trigger")
    trigger_conditions: Dict[str, Any] = Field(..., description="Trigger conditions and parameters")
    action_type: ActionType = Field(..., description="Type of action to execute")
    action_payload: Dict[str, Any] = Field(..., description="Action parameters and data")
    schedule_config: Optional[Dict[str, Any]] = Field(None, description="Scheduling configuration")
    is_active: bool = Field(default=True, description="Whether automation is active")
    priority: int = Field(default=1, ge=1, le=10, description="Execution priority (1=highest, 10=lowest)")


class AutomationUpdateRequest(BaseModel):
    """Schema for updating an automation."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    trigger_conditions: Optional[Dict[str, Any]] = None
    action_payload: Optional[Dict[str, Any]] = None
    schedule_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)


class AutomationRead(BaseModel):
    """Schema for reading an automation."""
    id: int
    name: str
    description: Optional[str]
    trigger_type: TriggerType
    trigger_conditions: Dict[str, Any]
    action_type: ActionType
    action_payload: Dict[str, Any]
    schedule_config: Optional[Dict[str, Any]]
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationListResponse(BaseModel):
    """Schema for automation list response."""
    automations: List[AutomationRead]
    total: int
    page: int
    size: int


class AutomationExecutionRequest(BaseModel):
    """Schema for manual automation execution."""
    automation_id: int = Field(..., description="ID of automation to execute")
    contact_id: Optional[int] = Field(None, description="Specific contact to target")
    test_mode: bool = Field(default=False, description="Whether this is a test execution")


class AutomationExecutionResponse(BaseModel):
    """Schema for automation execution response."""
    success: bool
    execution_id: Optional[int] = None
    message: str
    contacts_affected: int = 0
    execution_time: Optional[float] = None
    error: Optional[str] = None


class AutomationStatsResponse(BaseModel):
    """Schema for automation statistics."""
    total_automations: int
    active_automations: int
    inactive_automations: int
    executions_today: int
    executions_this_week: int
    executions_this_month: int
    success_rate: float
    average_execution_time: float


class AutomationLogRead(BaseModel):
    """Schema for reading automation logs."""
    id: int
    automation_id: int
    contact_id: Optional[int]
    execution_status: str
    execution_time: float
    contacts_affected: int
    error_message: Optional[str]
    execution_details: Optional[Dict[str, Any]]
    executed_at: datetime
    executed_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationLogListResponse(BaseModel):
    """Schema for automation log list response."""
    logs: List[AutomationLogRead]
    total: int
    page: int
    size: int


class AutomationSearchFilters(BaseModel):
    """Schema for automation search filters."""
    name: Optional[str] = None
    trigger_type: Optional[TriggerType] = None
    action_type: Optional[ActionType] = None
    is_active: Optional[bool] = None
    created_by: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class TriggerConditionExample(BaseModel):
    """Schema for trigger condition examples."""
    trigger_type: TriggerType
    example_conditions: Dict[str, Any]
    description: str


class ActionPayloadExample(BaseModel):
    """Schema for action payload examples."""
    action_type: ActionType
    example_payload: Dict[str, Any]
    description: str
