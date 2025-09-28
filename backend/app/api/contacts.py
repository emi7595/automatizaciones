"""
Contact API endpoints for managing contacts.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.contact import Contact
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)
router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("/{contact_id}")
@log_performance()
async def get_contact(
    contact_id: int = Path(..., description="Contact ID"),
    db: Session = Depends(get_db)
):
    """
    Get contact by ID.
    """
    logger.info(f"API: Getting contact: {contact_id}")
    
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {
            "success": True,
            "contact": {
                "id": contact.id,
                "name": contact.name,
                "phone": contact.phone,
                "email": contact.email,
                "birthday": contact.birthday.isoformat() if contact.birthday else None,
                "tags": contact.tags,
                "notes": contact.notes,
                "last_contacted": contact.last_contacted.isoformat() if contact.last_contacted else None,
                "is_active": contact.is_active,
                "created_at": contact.created_at.isoformat(),
                "updated_at": contact.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error getting contact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
@log_performance()
async def list_contacts(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(100, le=1000, description="Maximum number of contacts to return"),
    offset: int = Query(0, ge=0, description="Number of contacts to skip"),
    db: Session = Depends(get_db)
):
    """
    List contacts with optional filters.
    """
    logger.info(f"API: Listing contacts")
    
    try:
        query = db.query(Contact)
        
        if is_active is not None:
            query = query.filter(Contact.is_active == is_active)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag in tag_list:
                query = query.filter(Contact.tags.contains([tag]))
        
        contacts = query.offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "contacts": [
                {
                    "id": contact.id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "email": contact.email,
                    "birthday": contact.birthday.isoformat() if contact.birthday else None,
                    "tags": contact.tags,
                    "notes": contact.notes,
                    "last_contacted": contact.last_contacted.isoformat() if contact.last_contacted else None,
                    "is_active": contact.is_active,
                    "created_at": contact.created_at.isoformat(),
                    "updated_at": contact.updated_at.isoformat()
                }
                for contact in contacts
            ],
            "count": len(contacts),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"API: Error listing contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}")
@log_performance()
async def update_contact(
    contact_id: int = Path(..., description="Contact ID"),
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    birthday: Optional[str] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Update contact information.
    """
    logger.info(f"API: Updating contact: {contact_id}")
    
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Update fields if provided
        if name is not None:
            contact.name = name
        if phone is not None:
            contact.phone = phone
        if email is not None:
            contact.email = email
        if birthday is not None:
            contact.birthday = datetime.fromisoformat(birthday) if birthday else None
        if tags is not None:
            contact.tags = tags
        if notes is not None:
            contact.notes = notes
        if is_active is not None:
            contact.is_active = is_active
        
        contact.updated_at = datetime.now()
        db.commit()
        
        logger.info(f"API: Updated contact: {contact_id}")
        return {
            "success": True,
            "contact": {
                "id": contact.id,
                "name": contact.name,
                "phone": contact.phone,
                "email": contact.email,
                "birthday": contact.birthday.isoformat() if contact.birthday else None,
                "tags": contact.tags,
                "notes": contact.notes,
                "last_contacted": contact.last_contacted.isoformat() if contact.last_contacted else None,
                "is_active": contact.is_active,
                "created_at": contact.created_at.isoformat(),
                "updated_at": contact.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error updating contact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
