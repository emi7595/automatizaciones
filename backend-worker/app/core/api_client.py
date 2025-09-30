"""
API client for worker to communicate with backend services.
This allows the worker to use the backend's business logic instead of duplicating it.
"""
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class BackendAPIClient:
    """Client for communicating with backend API services."""
    
    def __init__(self):
        self.base_url = settings.BACKEND_API_URL
        self.timeout = 30.0
        self.logger = get_logger(__name__)
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)
                
                # Log request details for debugging
                self.logger.info(f"HTTP Request: {method} {url} \"{response.status_code} {response.reason_phrase}\"")
                
                # For 422 errors, log the detailed validation error
                if response.status_code == 422:
                    try:
                        error_details = response.json()
                        self.logger.error(f"Validation error details: {error_details}")
                    except:
                        self.logger.error(f"Could not parse 422 error response")
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in API request: {str(e)}")
            raise
    
    # Automation API methods
    async def get_automation(self, automation_id: int) -> Dict[str, Any]:
        """Get automation by ID."""
        return await self._make_request("GET", f"/api/automations/{automation_id}")
    
    async def list_automations(self, trigger_type: str = None, is_active: bool = None) -> Dict[str, Any]:
        """List automations with optional filters."""
        params = {}
        if trigger_type:
            params["trigger_type"] = trigger_type
        if is_active is not None:
            params["is_active"] = is_active
        
        return await self._make_request("GET", "/api/automations", params=params)
    
    async def execute_automation(self, automation_id: int, contact_id: int = None, user_id: int = None) -> Dict[str, Any]:
        """Execute automation for a specific contact."""
        data = {}
        if contact_id:
            data["contact_id"] = contact_id
        if user_id:
            data["user_id"] = user_id
        
        return await self._make_request("POST", f"/api/automations/{automation_id}/execute", json=data)
    
    async def get_automation_stats(self, automation_id: int) -> Dict[str, Any]:
        """Get automation statistics."""
        return await self._make_request("GET", f"/api/automations/{automation_id}/stats")
    
    # Contact API methods
    async def get_contact(self, contact_id: int) -> Dict[str, Any]:
        """Get contact by ID."""
        return await self._make_request("GET", f"/api/contacts/{contact_id}")
    
    async def list_contacts(self, is_active: bool = None, tags: List[str] = None) -> Dict[str, Any]:
        """List contacts with optional filters."""
        params = {}
        if is_active is not None:
            params["is_active"] = is_active
        if tags:
            params["tags"] = ",".join(tags)
        
        return await self._make_request("GET", "/api/contacts", params=params)
    
    async def update_contact(self, contact_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact information."""
        return await self._make_request("PUT", f"/api/contacts/{contact_id}", json=data)
    
    # Message API methods
    async def send_message(self, contact_id: int, content: str, message_type: str = "text", user_id: int = None) -> Dict[str, Any]:
        """Send message to contact."""
        data = {
            "contact_id": contact_id,
            "content": content,
            "message_type": message_type
        }
        if user_id:
            data["user_id"] = user_id
        
        # Log the exact data being sent for debugging
        self.logger.info(f"Sending message data: {data}")
        
        return await self._make_request("POST", "/api/messages/send", json=data)
    
    async def get_message(self, message_id: int) -> Dict[str, Any]:
        """Get message by ID."""
        return await self._make_request("GET", f"/api/messages/{message_id}")
    
    async def list_messages(self, contact_id: int = None, direction: str = None, limit: int = 100) -> Dict[str, Any]:
        """List messages with optional filters."""
        params = {"limit": limit}
        if contact_id:
            params["contact_id"] = contact_id
        if direction:
            params["direction"] = direction
        
        return await self._make_request("GET", "/api/messages", params=params)
    
    # Analytics API methods
    async def record_automation_execution(self, automation_id: int, contact_id: int, status: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Record automation execution in analytics."""
        data = {
            "automation_id": automation_id,
            "contact_id": contact_id,
            "status": status
        }
        if details:
            data["details"] = details
        
        return await self._make_request("POST", "/api/analytics/automation-execution", json=data)
    
    async def update_contact_analytics(self, contact_id: int, metric_type: str, metric_value: float, dimensions: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update contact analytics."""
        data = {
            "contact_id": contact_id,
            "metric_type": metric_type,
            "metric_value": metric_value
        }
        if dimensions:
            data["dimensions"] = dimensions
        
        return await self._make_request("POST", "/api/analytics/contact-metrics", json=data)


# Global API client instance
api_client = BackendAPIClient()


# Convenience functions for common operations
async def get_automation_by_id(automation_id: int) -> Dict[str, Any]:
    """Get automation by ID."""
    return await api_client.get_automation(automation_id)


async def get_automations_by_trigger(trigger_type: str) -> List[Dict[str, Any]]:
    """Get automations by trigger type."""
    response = await api_client.list_automations(trigger_type=trigger_type, is_active=True)
    return response.get("automations", [])


async def execute_automation_for_contact(automation_id: int, contact_id: int, user_id: int = None) -> Dict[str, Any]:
    """Execute automation for a specific contact."""
    return await api_client.execute_automation(automation_id, contact_id, user_id)


async def send_message_to_contact(contact_id: int, content: str, message_type: str = "text", user_id: int = None) -> Dict[str, Any]:
    """Send message to contact."""
    return await api_client.send_message(contact_id, content, message_type, user_id)


async def get_contact_by_id(contact_id: int) -> Dict[str, Any]:
    """Get contact by ID."""
    return await api_client.get_contact(contact_id)


async def get_contacts_by_criteria(is_active: bool = True, tags: List[str] = None) -> List[Dict[str, Any]]:
    """Get contacts by criteria."""
    response = await api_client.list_contacts(is_active=is_active, tags=tags)
    return response.get("contacts", [])


async def record_automation_result(automation_id: int, contact_id: int, status: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Record automation execution result."""
    return await api_client.record_automation_execution(automation_id, contact_id, status, details)


async def update_message_status(whatsapp_message_id: str, status: str, timestamp: int = None) -> Dict[str, Any]:
    """Update message status via backend API."""
    data = {"status": status}
    if timestamp:
        data["timestamp"] = timestamp
    
    return await api_client._make_request("PUT", f"/api/messages/status/{whatsapp_message_id}", json=data)


async def send_whatsapp_message(contact_id: int, content: str, message_type: str = "text", user_id: int = None) -> Dict[str, Any]:
    """Send WhatsApp message via backend API."""
    return await api_client.send_message(contact_id, content, message_type, user_id)


async def get_failed_messages() -> Dict[str, Any]:
    """Get failed messages from backend API."""
    return await api_client._make_request("GET", "/api/messages/failed")
