"""
Pydantic schemas for message-related API operations.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.message import MessageDirection, MessageType, MessageStatus


class MessageSendRequest(BaseModel):
    """Schema for sending a WhatsApp message."""
    contact_id: int = Field(..., description="ID of the contact to send message to")
    content: str = Field(..., min_length=1, max_length=4096, description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")


class MessageSendResponse(BaseModel):
    """Schema for message send response."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    whatsapp_message_id: Optional[str] = None


class MessageRead(BaseModel):
    """Schema for reading a message."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    contact_id: int
    conversation_id: str
    direction: MessageDirection
    message_type: MessageType
    content: str
    whatsapp_message_id: Optional[str]
    status: MessageStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias='extra_metadata')
    created_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for message list response."""
    messages: List[MessageRead]
    total: int
    page: int
    size: int


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    conversation_id: str
    contact_id: int
    contact_name: str
    contact_phone: str
    last_message: Optional[MessageRead]
    message_count: int
    last_activity: Optional[datetime]
    unread_count: int


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""
    conversations: List[ConversationResponse]
    total: int
    page: int
    size: int


class MessageStatusUpdate(BaseModel):
    """Schema for updating message status."""
    status: MessageStatus
    timestamp: Optional[datetime] = None
    error_message: Optional[str] = None


class WebhookMessageData(BaseModel):
    """Schema for incoming webhook message data."""
    message_id: str
    from_number: str
    content: str
    message_type: str
    timestamp: int
    raw_data: Dict[str, Any]


class WebhookStatusData(BaseModel):
    """Schema for incoming webhook status data."""
    message_id: str
    status: str
    timestamp: int
    recipient_id: str
    raw_data: Dict[str, Any]


class TemplateMessageRequest(BaseModel):
    """Schema for sending a template message."""
    contact_id: int = Field(..., description="ID of the contact to send message to")
    template_name: str = Field(..., description="Name of the WhatsApp template")
    language: str = Field(default="en", description="Template language code")
    components: Optional[List[Dict[str, Any]]] = Field(default=None, description="Template components")


class MessageSearchFilters(BaseModel):
    """Schema for message search filters."""
    contact_id: Optional[int] = None
    conversation_id: Optional[str] = None
    direction: Optional[MessageDirection] = None
    message_type: Optional[MessageType] = None
    status: Optional[MessageStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
