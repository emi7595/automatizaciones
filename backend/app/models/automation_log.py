"""
Automation log model for tracking automation executions.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SAEnum, Float
from sqlalchemy.sql import func
from app.database import Base
import enum


class ExecutionStatus(str, enum.Enum):
    """Automation execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class AutomationLog(Base):
    """Automation log for tracking execution history and performance."""
    
    __tablename__ = "automation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)  # Null for bulk operations
    execution_status = Column(
        SAEnum(
            ExecutionStatus,
            values_callable=lambda x: [e.value for e in x],
            validate_strings=True
        ),
        nullable=False
    )
    execution_time = Column(Float, nullable=True)  # Execution time in seconds
    contacts_affected = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_details = Column(JSON, nullable=True)  # Detailed execution information
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    executed_by = Column(String(50), default="system", nullable=False)  # "system" or user identifier
    
    def __repr__(self):
        return f"<AutomationLog(id={self.id}, automation_id={self.automation_id}, status='{self.execution_status}')>"
    
    def get_execution_details(self) -> dict:
        """Get execution details as dictionary."""
        return self.execution_details or {}
    
    def add_execution_detail(self, key: str, value):
        """Add a detail to execution_details."""
        if self.execution_details is None:
            self.execution_details = {}
        self.execution_details[key] = value
