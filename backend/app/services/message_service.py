"""
Message service for managing WhatsApp messages and conversations.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.message import Message, MessageDirection, MessageType, MessageStatus
from app.models.contact import Contact
from app.schemas.message import (
    MessageSendRequest, MessageSearchFilters, ConversationResponse
)
from app.services.whatsapp_service import whatsapp_service
from app.tasks.message_tasks import process_message_status_update
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)


class MessageService:
    """Service for managing messages and conversations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    @log_performance()
    async def send_message(self, request: MessageSendRequest, user_id: int) -> Dict[str, Any]:
        """
        Send a WhatsApp message to a contact.
        
        Args:
            request: Message send request
            user_id: ID of the user sending the message
            
        Returns:
            Dict containing send result and message data
        """
        logger.info(f"Processing message send request for contact {request.contact_id}")
        logger.debug(f"Request details: {request}")
        
        try:
            # Get contact information
            logger.debug(f"Looking up contact {request.contact_id}")
            contact = self.db.query(Contact).filter(Contact.id == request.contact_id).first()
            if not contact:
                logger.error(f"Contact {request.contact_id} not found")
                return {"success": False, "error": "Contact not found"}
            
            if not contact.is_active:
                logger.error(f"Contact {request.contact_id} is not active")
                return {"success": False, "error": "Contact is not active"}
            
            logger.info(f"Found contact: {contact.name} ({contact.phone})")
            
            # Clean phone number (remove + and spaces)
            phone_number = contact.phone.replace("+", "").replace(" ", "")
            logger.debug(f"Cleaned phone number: {phone_number}")
            
            # Send message via WhatsApp API
            if request.message_type == MessageType.TEXT:
                logger.info(f"Sending text message via WhatsApp API")
                result = await whatsapp_service.send_text_message(phone_number, request.content)
            else:
                logger.error(f"Message type {request.message_type} not supported yet")
                return {"success": False, "error": f"Message type {request.message_type} not supported yet"}
            
            if not result["success"]:
                logger.error(f"WhatsApp API call failed: {result['error']}")
                return result
            
            logger.info(f"WhatsApp API call successful: {result['message_id']}")
            
            # Create message record in database
            conversation_id = self._get_or_create_conversation_id(contact.id)
            logger.debug(f"Using conversation ID: {conversation_id}")
            
            message = Message(
                contact_id=request.contact_id,
                conversation_id=conversation_id,
                direction=MessageDirection.OUTBOUND,
                message_type=request.message_type,
                content=request.content,
                whatsapp_message_id=result["message_id"],
                status=MessageStatus.SENT,
                sent_at=datetime.now(),
                extra_metadata=request.metadata,
                created_by=user_id
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Message record created in database: {message.id}")
            
            # Update contact's last_contacted timestamp
            contact.last_contacted = datetime.now()
            self.db.commit()
            
            logger.info(f"Message sent successfully: {message.id} to contact {contact.id}")
            logger.debug(f"Message details: {message}")
            
            return {
                "success": True,
                "message_id": message.id,
                "whatsapp_message_id": result["message_id"],
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            logger.exception("Full error traceback:")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    async def send_template_message(self, contact_id: int, template_name: str, 
                                 language: str = "en", components: List[Dict] = None,
                                 user_id: int = None) -> Dict[str, Any]:
        """
        Send a WhatsApp template message to a contact.
        
        Args:
            contact_id: ID of the contact
            template_name: Name of the template
            language: Template language
            components: Template components
            user_id: ID of the user sending the message
            
        Returns:
            Dict containing send result and message data
        """
        try:
            # Get contact information
            contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            if not contact.is_active:
                return {"success": False, "error": "Contact is not active"}
            
            # Clean phone number
            phone_number = contact.phone.replace("+", "").replace(" ", "")
            
            # Send template message via WhatsApp API
            result = await whatsapp_service.send_template_message(
                phone_number, template_name, language, components
            )
            
            if not result["success"]:
                return result
            
            # Create message record
            message = Message(
                contact_id=contact_id,
                conversation_id=self._get_or_create_conversation_id(contact.id),
                direction=MessageDirection.OUTBOUND,
                message_type=MessageType.TEMPLATE,
                content=f"Template: {template_name}",
                whatsapp_message_id=result["message_id"],
                status=MessageStatus.SENT,
                sent_at=datetime.now(),
                extra_metadata={
                    "template_name": template_name,
                    "language": language,
                    "components": components
                },
                created_by=user_id
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            # Update contact's last_contacted timestamp
            contact.last_contacted = datetime.now()
            self.db.commit()
            
            logger.info(f"Template message sent successfully: {message.id} to contact {contact.id}")
            
            return {
                "success": True,
                "message_id": message.id,
                "whatsapp_message_id": result["message_id"],
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error sending template message: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_messages(self, filters: MessageSearchFilters) -> Dict[str, Any]:
        """
        Get messages with optional filtering and pagination.
        
        Args:
            filters: Search filters and pagination
            
        Returns:
            Dict containing messages and pagination info
        """
        try:
            query = self.db.query(Message)
            
            # Apply filters
            if filters.contact_id:
                query = query.filter(Message.contact_id == filters.contact_id)
            
            if filters.conversation_id:
                query = query.filter(Message.conversation_id == filters.conversation_id)
            
            if filters.direction:
                query = query.filter(Message.direction == filters.direction)
            
            if filters.message_type:
                query = query.filter(Message.message_type == filters.message_type)
            
            if filters.status:
                query = query.filter(Message.status == filters.status)
            
            if filters.date_from:
                query = query.filter(Message.created_at >= filters.date_from)
            
            if filters.date_to:
                query = query.filter(Message.created_at <= filters.date_to)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(Message.content.ilike(search_term))
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            messages = query.order_by(desc(Message.created_at))\
                          .offset((filters.page - 1) * filters.size)\
                          .limit(filters.size)\
                          .all()
            
            return {
                "success": True,
                "messages": messages,
                "total": total,
                "page": filters.page,
                "size": filters.size
            }
            
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_conversations(self, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """
        Get conversations with contact information and message counts.
        
        Args:
            page: Page number
            size: Page size
            
        Returns:
            Dict containing conversations and pagination info
        """
        try:
            # Get conversations with contact info and message counts
            conversations_query = self.db.query(
                Message.conversation_id,
                Message.contact_id,
                Contact.name.label('contact_name'),
                Contact.phone.label('contact_phone'),
                func.max(Message.created_at).label('last_activity'),
                func.count(Message.id).label('message_count'),
                func.count(
                    and_(
                        Message.direction == MessageDirection.INBOUND,
                        Message.read_at.is_(None)
                    )
                ).label('unread_count')
            ).join(Contact, Message.contact_id == Contact.id)\
             .group_by(Message.conversation_id, Message.contact_id, Contact.name, Contact.phone)\
             .order_by(desc('last_activity'))
            
            # Get total count
            total = conversations_query.count()
            
            # Apply pagination
            conversations = conversations_query.offset((page - 1) * size).limit(size).all()
            
            # Get last message for each conversation
            conversation_list = []
            for conv in conversations:
                last_message = self.db.query(Message)\
                    .filter(Message.conversation_id == conv.conversation_id)\
                    .order_by(desc(Message.created_at))\
                    .first()
                
                conversation_list.append(ConversationResponse(
                    conversation_id=conv.conversation_id,
                    contact_id=conv.contact_id,
                    contact_name=conv.contact_name,
                    contact_phone=conv.contact_phone,
                    last_message=last_message,
                    message_count=conv.message_count,
                    last_activity=conv.last_activity,
                    unread_count=conv.unread_count
                ))
            
            return {
                "success": True,
                "conversations": conversation_list,
                "total": total,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_conversation_messages(self, conversation_id: str, page: int = 1, size: int = 50) -> Dict[str, Any]:
        """
        Get messages for a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            page: Page number
            size: Page size
            
        Returns:
            Dict containing messages and pagination info
        """
        try:
            query = self.db.query(Message).filter(Message.conversation_id == conversation_id)
            
            # Get total count
            total = query.count()
            
            # Get messages with pagination
            messages = query.order_by(Message.created_at)\
                          .offset((page - 1) * size)\
                          .limit(size)\
                          .all()
            
            return {
                "success": True,
                "messages": messages,
                "total": total,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_incoming_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message from WhatsApp webhook.
        
        Args:
            message_data: Processed message data from webhook
            
        Returns:
            Dict containing processing result
        """
        try:
            # Find or create contact
            contact = self.db.query(Contact).filter(
                Contact.phone == f"+{message_data['from_number']}"
            ).first()
            
            if not contact:
                # Create new contact for incoming message
                contact = Contact(
                    name=f"Contact {message_data['from_number']}",
                    phone=f"+{message_data['from_number']}",
                    is_active=True,
                    created_by=1  # System user
                )
                self.db.add(contact)
                self.db.commit()
                self.db.refresh(contact)
                logger.info(f"Created new contact for incoming message: {contact.id}")
            
            # Create message record
            message = Message(
                contact_id=contact.id,
                conversation_id=self._get_or_create_conversation_id(contact.id),
                direction=MessageDirection.INBOUND,
                message_type=MessageType(message_data['message_type']),
                content=message_data['content'],
                whatsapp_message_id=message_data['message_id'],
                status=MessageStatus.DELIVERED,
                sent_at=datetime.fromtimestamp(int(message_data['timestamp'])),
                extra_metadata=message_data.get('raw_data', {}),
                created_by=None  # Incoming message
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            # Update contact's last_contacted timestamp
            contact.last_contacted = datetime.now()
            self.db.commit()
            
            logger.info(f"Incoming message processed: {message.id} from contact {contact.id}")
            
            # Trigger message-based automations (queued for worker)
            try:
                from app.core.task_queue import TaskQueue
                TaskQueue.queue_message_automation(message.id)
            except Exception as e:
                logger.error(f"Error queuing message automation: {str(e)}")
            
            return {
                "success": True,
                "message_id": message.id,
                "contact_id": contact.id,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    async def update_message_status(self, whatsapp_message_id: str, status: str, 
                                  timestamp: int = None) -> Dict[str, Any]:
        """
        Update message status based on WhatsApp webhook.
        
        Args:
            whatsapp_message_id: WhatsApp message ID
            status: New status
            timestamp: Status timestamp
            
        Returns:
            Dict containing update result
        """
        try:
            # Find message by WhatsApp message ID
            message = self.db.query(Message).filter(
                Message.whatsapp_message_id == whatsapp_message_id
            ).first()
            
            if not message:
                return {"success": False, "error": "Message not found"}
            
            # Update status
            old_status = message.status
            message.status = MessageStatus(status)
            
            if timestamp:
                status_time = datetime.fromtimestamp(timestamp)
                if status == "delivered":
                    message.delivered_at = status_time
                elif status == "read":
                    message.read_at = status_time
            
            self.db.commit()
            
            logger.info(f"Message status updated: {message.id} from {old_status} to {status}")
            
            return {
                "success": True,
                "message_id": message.id,
                "old_status": old_status,
                "new_status": status
            }
            
        except Exception as e:
            logger.error(f"Error updating message status: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _get_or_create_conversation_id(self, contact_id: int) -> str:
        """
        Get or create conversation ID for a contact.
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Conversation ID
        """
        # Check if contact already has a conversation
        existing_message = self.db.query(Message).filter(
            Message.contact_id == contact_id
        ).first()
        
        if existing_message:
            return existing_message.conversation_id
        
        # Create new conversation ID
        import uuid
        return str(uuid.uuid4())
