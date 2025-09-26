"""
WhatsApp Cloud API service for sending and receiving messages.
"""
import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.config import settings
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)


class WhatsAppService:
    """WhatsApp Cloud API service for message operations."""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_TOKEN
        self.business_id = settings.BUSINESS_ID
        self.verify_token = settings.WEBHOOK_VERIFY_TOKEN
        
        logger.info("Initializing WhatsApp Service")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Phone Number ID: {self.phone_number_id}")
        logger.info(f"Business ID: {self.business_id}")
        logger.info(f"Access Token configured: {bool(self.access_token)}")
        logger.info(f"Verify Token configured: {bool(self.verify_token)}")
        
        if not all([self.phone_number_id, self.access_token, self.business_id]):
            logger.warning("WhatsApp configuration incomplete. Some features may not work.")
        else:
            logger.info("WhatsApp Service configuration complete")
    
    @log_performance()
    async def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp Cloud API.
        
        Args:
            to: Recipient phone number (with country code, no +)
            message: Text message content
            
        Returns:
            Dict containing API response and message ID
        """
        logger.info(f"Sending text message to {to}")
        logger.debug(f"Message content: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            logger.debug(f"API URL: {url}")
            logger.debug(f"Payload: {payload}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id')
                logger.info(f"Message sent successfully to {to}: {message_id}")
                logger.debug(f"Full API response: {result}")
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "response": result
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending message to {to}: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "message_id": None
            }
        except Exception as e:
            logger.error(f"Error sending message to {to}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None
            }
    
    async def send_template_message(self, to: str, template_name: str, 
                                  language: str = "en", components: List[Dict] = None) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp Cloud API.
        
        Args:
            to: Recipient phone number
            template_name: Name of the template
            language: Template language code
            components: Template components (parameters, buttons, etc.)
            
        Returns:
            Dict containing API response and message ID
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language
                    },
                    "components": components or []
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Template message sent successfully to {to}: {result.get('messages', [{}])[0].get('id')}")
                logger.debug(f"Full API response: {result}")
                
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "response": result
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending template to {to}: {e.response.status_code} - {e.response.text}")
            logger.error(f"Response text: {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "message_id": None
            }
        except Exception as e:
            logger.error(f"Error sending template to {to}: {str(e)}")
            logger.error(f"Response text: {e.response.text}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None
            }
    
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a sent message.
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            Dict containing message status information
        """
        try:
            url = f"{self.base_url}/{message_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                return {
                    "success": True,
                    "status": result.get("status"),
                    "response": result
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting message status {message_id}: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "status": None
            }
        except Exception as e:
            logger.error(f"Error getting message status {message_id}: {str(e)}")
            logger.error(f"Response text: {e.response.text}")
            return {
                "success": False,
                "error": str(e),
                "status": None
            }
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook subscription with Meta.
        
        Args:
            mode: Verification mode from Meta
            token: Verification token from Meta
            challenge: Challenge string from Meta
            
        Returns:
            Challenge string if verification successful, None otherwise
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook verification successful")
            return challenge
        else:
            logger.warning(f"Webhook verification failed: mode={mode}, token={token}")
            return None
    
    async def process_incoming_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming webhook data from WhatsApp.
        
        Args:
            webhook_data: Raw webhook data from Meta
            
        Returns:
            Dict containing processed message information
        """
        try:
            # Extract message data from webhook
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return {"success": False, "error": "No messages in webhook data"}
            
            message = messages[0]
            message_id = message.get("id")
            from_number = message.get("from")
            timestamp = message.get("timestamp")
            
            # Extract message content based on type
            message_type = message.get("type")
            content = ""
            
            if message_type == "text":
                content = message.get("text", {}).get("body", "")
            elif message_type == "image":
                content = f"[Image: {message.get('image', {}).get('id', 'unknown')}]"
            elif message_type == "document":
                content = f"[Document: {message.get('document', {}).get('filename', 'unknown')}]"
            else:
                content = f"[{message_type.title()}]"
            
            return {
                "success": True,
                "message_id": message_id,
                "from_number": from_number,
                "content": content,
                "message_type": message_type,
                "timestamp": timestamp,
                "raw_data": message
            }
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
            logger.error(f"Response text: {e.response.text}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_status_update(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process status update webhook data from WhatsApp.
        
        Args:
            webhook_data: Raw webhook data from Meta
            
        Returns:
            Dict containing processed status information
        """
        try:
            # Extract status data from webhook
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            statuses = value.get("statuses", [])
            
            if not statuses:
                return {"success": False, "error": "No statuses in webhook data"}
            
            status = statuses[0]
            message_id = status.get("id")
            status_type = status.get("status")
            timestamp = status.get("timestamp")
            recipient_id = status.get("recipient_id")
            
            return {
                "success": True,
                "message_id": message_id,
                "status": status_type,
                "timestamp": timestamp,
                "recipient_id": recipient_id,
                "raw_data": status
            }
            
        except Exception as e:
            logger.error(f"Error processing status update: {str(e)}")
            logger.error(f"Response text: {e.response.text}")
            return {
                "success": False,
                "error": str(e)
            }


# Global WhatsApp service instance
whatsapp_service = WhatsAppService()
