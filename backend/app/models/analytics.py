"""
Analytics model for tracking various metrics and performance data.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class MetricType(str, enum.Enum):
    """Analytics metric types."""
    MESSAGE_DELIVERY = "message_delivery"
    AUTOMATION_PERFORMANCE = "automation_performance"
    CONTACT_ENGAGEMENT = "contact_engagement"
    SYSTEM_PERFORMANCE = "system_performance"
    USER_ACTIVITY = "user_activity"


class Analytics(Base):
    """Analytics model for comprehensive metrics tracking."""
    
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    dimensions = Column(JSON, nullable=True)  # Flexible dimensions for filtering
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=True, index=True)  # For time-based metrics
    period_end = Column(DateTime(timezone=True), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Analytics(id={self.id}, type='{self.metric_type}', name='{self.metric_name}')>"
    
    def get_dimensions(self) -> dict:
        """Get dimensions as dictionary."""
        return self.dimensions or {}
    
    def add_dimension(self, key: str, value):
        """Add a dimension."""
        if self.dimensions is None:
            self.dimensions = {}
        self.dimensions[key] = value
