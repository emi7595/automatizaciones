"""
Webhook endpoints for receiving WhatsApp messages and status updates.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db
from app.services.whatsapp_service import whatsapp_service
from app.services.message_service import MessageService
from app.schemas.message import WebhookMessageData, WebhookStatusData
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/whatsapp")
@log_performance()
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """
    Verify WhatsApp webhook subscription with Meta.
    This endpoint is called by Meta to verify the webhook URL.
    """
    logger.info(f"Webhook verification request received")
    logger.debug(f"Mode: {hub_mode}, Challenge: {hub_challenge}, Token: {hub_verify_token[:10]}...")
    
    try:
        challenge = whatsapp_service.verify_webhook(
            mode=hub_mode,
            token=hub_verify_token,
            challenge=hub_challenge
        )
        
        if challenge:
            logger.info("Webhook verification successful")
            return int(challenge)
        else:
            logger.warning("Webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook verification error: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp")
@log_performance()
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive WhatsApp webhook data from Meta.
    This endpoint processes incoming messages and status updates.
    """
    logger.info(f"Webhook data received from Meta")
    
    try:
        # Get raw webhook data
        webhook_data = await request.json()
        logger.info(f"Webhook data structure: {list(webhook_data.keys())}")
        logger.debug(f"Full webhook data: {webhook_data}")
        
        # Process webhook data
        result = await _process_webhook_data(webhook_data, db)
        
        logger.info(f"Webhook processing completed: {result}")
        return {"status": "success", "processed": result}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        logger.exception("Full error traceback:")
        # Don't raise HTTPException here as Meta expects 200 response
        return {"status": "error", "error": str(e)}


async def _process_webhook_data(webhook_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Process webhook data and route to appropriate handlers.
    
    Args:
        webhook_data: Raw webhook data from Meta
        db: Database session
        
    Returns:
        Dict containing processing results
    """
    try:
        results = {
            "messages_processed": 0,
            "statuses_processed": 0,
            "errors": []
        }
        
        # Extract entry data
        entry = webhook_data.get("entry", [])
        
        for entry_data in entry:
            changes = entry_data.get("changes", [])
            
            for change in changes:
                value = change.get("value", {})
                
                # Process messages (incoming messages)
                messages = value.get("messages", [])
                for message_data in messages:
                    try:
                        # Process incoming message
                        processed_message = await whatsapp_service.process_incoming_message({
                            "entry": [entry_data],
                            "changes": [change]
                        })
                        
                        if processed_message["success"]:
                            # Store message in database
                            message_service = MessageService(db)
                            db_result = await message_service.process_incoming_message(processed_message)
                            
                            if db_result["success"]:
                                results["messages_processed"] += 1
                                logger.info(f"Message processed successfully: {db_result['message_id']}")
                            else:
                                results["errors"].append(f"Database error: {db_result['error']}")
                        else:
                            results["errors"].append(f"Message processing error: {processed_message['error']}")
                            
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        results["errors"].append(f"Message processing error: {str(e)}")
                
                # Process statuses (message status updates)
                statuses = value.get("statuses", [])
                for status_data in statuses:
                    try:
                        # Process status update
                        processed_status = await whatsapp_service.process_status_update({
                            "entry": [entry_data],
                            "changes": [change]
                        })
                        
                        if processed_status["success"]:
                            # Update message status in database
                            message_service = MessageService(db)
                            db_result = await message_service.update_message_status(
                                whatsapp_message_id=processed_status["message_id"],
                                status=processed_status["status"],
                                timestamp=processed_status["timestamp"]
                            )
                            
                            if db_result["success"]:
                                results["statuses_processed"] += 1
                                logger.info(f"Status updated successfully: {db_result['message_id']}")
                            else:
                                results["errors"].append(f"Database error: {db_result['error']}")
                        else:
                            results["errors"].append(f"Status processing error: {processed_status['error']}")
                            
                    except Exception as e:
                        logger.error(f"Error processing status: {str(e)}")
                        results["errors"].append(f"Status processing error: {str(e)}")
        
        logger.info(f"Webhook processing completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Error processing webhook data: {str(e)}")
        return {
            "messages_processed": 0,
            "statuses_processed": 0,
            "errors": [str(e)]
        }


@router.post("/whatsapp/test")
async def test_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Test webhook endpoint for development and debugging.
    """
    try:
        webhook_data = await request.json()
        logger.info(f"Test webhook received: {webhook_data}")
        
        # Process test data
        result = await _process_webhook_data(webhook_data, db)
        
        return {
            "status": "test_success",
            "processed": result,
            "webhook_data": webhook_data
        }
        
    except Exception as e:
        logger.error(f"Test webhook error: {str(e)}")
        return {
            "status": "test_error",
            "error": str(e)
        }
