"""
Message model with threading support and comprehensive metadata.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid


class MessageDirection(str, enum.Enum):
    """Message direction enumeration."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageType(str, enum.Enum):
    """Message type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    TEMPLATE = "template"


class MessageStatus(str, enum.Enum):
    """Message status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(Base):
    """Message model with threading and comprehensive tracking."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    conversation_id = Column(String(36), nullable=False, index=True)  # UUID for threading
    direction = Column(Enum(MessageDirection), nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=False)
    whatsapp_message_id = Column(String(100), nullable=True, index=True)  # WhatsApp API message ID
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSON, nullable=True)  # Flexible metadata storage
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for inbound messages
    
    def __repr__(self):
        return f"<Message(id={self.id}, contact_id={self.contact_id}, direction='{self.direction}')>"
    
    @classmethod
    def create_conversation_id(cls) -> str:
        """Generate a new conversation UUID."""
        return str(uuid.uuid4())
    
    def update_status(self, status: MessageStatus, timestamp: DateTime = None):
        """Update message status with appropriate timestamp."""
        self.status = status
        if timestamp is None:
            timestamp = func.now()
        
        if status == MessageStatus.SENT:
            self.sent_at = timestamp
        elif status == MessageStatus.DELIVERED:
            self.delivered_at = timestamp
        elif status == MessageStatus.READ:
            self.read_at = timestamp
