"""
Message API endpoints for WhatsApp message management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.message import (
    MessageSendRequest, MessageSendResponse, MessageRead, MessageListResponse,
    ConversationResponse, ConversationListResponse, MessageSearchFilters,
    TemplateMessageRequest
)
from app.services.message_service import MessageService
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)
router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/send", response_model=MessageSendResponse)
@log_performance()
async def send_message(
    request: MessageSendRequest,
    db: Session = Depends(get_db)
):
    """
    Send a WhatsApp message to a contact.
    """
    logger.info(f"API: Send message request received")
    logger.debug(f"Request: {request}")
    
    try:
        message_service = MessageService(db)
        result = await message_service.send_message(request, user_id=1)  # TODO: Get from auth
        
        if not result["success"]:
            logger.error(f"API: Message send failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"API: Message sent successfully: {result['message_id']}")
        return MessageSendResponse(
            success=True,
            message_id=result["message_id"],
            whatsapp_message_id=result["whatsapp_message_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error in send_message: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-template", response_model=MessageSendResponse)
async def send_template_message(
    request: TemplateMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a WhatsApp template message to a contact.
    """
    try:
        message_service = MessageService(db)
        result = await message_service.send_template_message(
            contact_id=request.contact_id,
            template_name=request.template_name,
            language=request.language,
            components=request.components,
            user_id=1  # TODO: Get from auth
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return MessageSendResponse(
            success=True,
            message_id=result["message_id"],
            whatsapp_message_id=result["whatsapp_message_id"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=MessageListResponse)
async def get_messages(
    contact_id: Optional[int] = Query(None, description="Filter by contact ID"),
    conversation_id: Optional[str] = Query(None, description="Filter by conversation ID"),
    direction: Optional[str] = Query(None, description="Filter by direction (inbound/outbound)"),
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in message content"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get messages with optional filtering and pagination.
    """
    try:
        filters = MessageSearchFilters(
            contact_id=contact_id,
            conversation_id=conversation_id,
            direction=direction,
            message_type=message_type,
            status=status,
            search=search,
            page=page,
            size=size
        )
        
        message_service = MessageService(db)
        result = message_service.get_messages(filters)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return MessageListResponse(
            messages=result["messages"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{message_id}", response_model=MessageRead)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific message by ID.
    """
    try:
        from app.models.message import Message
        
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/", response_model=ConversationListResponse)
async def get_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get all conversations with contact information.
    """
    try:
        message_service = MessageService(db)
        result = message_service.get_conversations(page=page, size=size)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ConversationListResponse(
            conversations=result["conversations"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get messages for a specific conversation.
    """
    try:
        message_service = MessageService(db)
        result = message_service.get_conversation_messages(
            conversation_id=conversation_id,
            page=page,
            size=size
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return MessageListResponse(
            messages=result["messages"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{message_id}/status")
async def update_message_status(
    message_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update message status (for testing purposes).
    """
    try:
        from app.models.message import Message, MessageStatus
        
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Update status
        old_status = message.status
        message.status = MessageStatus(status)
        
        if status == "delivered":
            message.delivered_at = datetime.now()
        elif status == "read":
            message.read_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message_id": message_id,
            "old_status": old_status,
            "new_status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
