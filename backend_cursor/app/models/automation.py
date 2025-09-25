"""
Automation model with comprehensive trigger and action support.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class TriggerType(str, enum.Enum):
    """Automation trigger types."""
    NEW_CONTACT = "new_contact"
    BIRTHDAY = "birthday"
    MESSAGE_RECEIVED = "message_received"
    SCHEDULED = "scheduled"
    KEYWORD = "keyword"
    TIME_BASED = "time_based"
    MANUAL = "manual"


class ActionType(str, enum.Enum):
    """Automation action types."""
    SEND_MESSAGE = "send_message"
    ADD_TO_GROUP = "add_to_group"
    UPDATE_CONTACT = "update_contact"
    TRIGGER_AUTOMATION = "trigger_automation"
    SEND_EMAIL = "send_email"
    LOG_ACTIVITY = "log_activity"


class Automation(Base):
    """Automation model with flexible trigger and action configuration."""
    
    __tablename__ = "automations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(
        SAEnum(
            TriggerType,
            values_callable=lambda x: [e.value for e in x],
            validate_strings=True
        ),
        nullable=False
    )
    trigger_conditions = Column(JSON, nullable=True)  # Flexible trigger conditions
    action_type = Column(
        SAEnum(
            ActionType,
            values_callable=lambda x: [e.value for e in x],
            validate_strings=True
        ),
        nullable=False
    )
    action_payload = Column(JSON, nullable=False)  # Action configuration
    schedule_config = Column(JSON, nullable=True)  # For scheduled/recurring automations
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=1, nullable=False)  # Execution priority (1-10)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    def __repr__(self):
        return f"<Automation(id={self.id}, name='{self.name}', trigger='{self.trigger_type}')>"
    
    def get_trigger_conditions(self) -> dict:
        """Get trigger conditions as dictionary."""
        return self.trigger_conditions or {}
    
    def get_action_payload(self) -> dict:
        """Get action payload as dictionary."""
        return self.action_payload or {}
    
    def get_schedule_config(self) -> dict:
        """Get schedule configuration as dictionary."""
        return self.schedule_config or {}
