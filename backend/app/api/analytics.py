"""
Analytics API endpoints for recording metrics and automation execution data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models.analytics import Analytics, MetricType
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/automation-execution")
@log_performance()
async def record_automation_execution(
    automation_id: int,
    contact_id: int,
    status: str,
    details: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Record automation execution in analytics.
    """
    logger.info(f"API: Recording automation execution: {automation_id} -> {contact_id} ({status})")
    
    try:
        # Create analytics record
        analytics = Analytics(
            metric_type=MetricType.AUTOMATION_EXECUTION,
            metric_name="automation_execution",
            metric_value=1.0 if status == "success" else 0.0,
            dimensions={
                "automation_id": automation_id,
                "contact_id": contact_id,
                "status": status,
                "details": details or {}
            },
            recorded_at=datetime.now()
        )
        
        db.add(analytics)
        db.commit()
        
        logger.info(f"API: Recorded automation execution analytics: {analytics.id}")
        return {
            "success": True,
            "analytics_id": analytics.id,
            "message": "Automation execution recorded"
        }
        
    except Exception as e:
        logger.error(f"API: Error recording automation execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contact-metrics")
@log_performance()
async def update_contact_analytics(
    contact_id: int,
    metric_type: str,
    metric_value: float,
    dimensions: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Update contact analytics metrics.
    """
    logger.info(f"API: Updating contact analytics: {contact_id} -> {metric_type} = {metric_value}")
    
    try:
        # Create analytics record
        analytics = Analytics(
            metric_type=MetricType(metric_type),
            metric_name=f"contact_{metric_type}",
            metric_value=metric_value,
            dimensions={
                "contact_id": contact_id,
                **(dimensions or {})
            },
            recorded_at=datetime.now()
        )
        
        db.add(analytics)
        db.commit()
        
        logger.info(f"API: Recorded contact analytics: {analytics.id}")
        return {
            "success": True,
            "analytics_id": analytics.id,
            "message": "Contact metrics updated"
        }
        
    except Exception as e:
        logger.error(f"API: Error updating contact analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
@log_performance()
async def get_analytics_metrics(
    metric_type: Optional[str] = None,
    contact_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get analytics metrics with optional filters.
    """
    logger.info(f"API: Getting analytics metrics")
    
    try:
        query = db.query(Analytics)
        
        if metric_type:
            query = query.filter(Analytics.metric_type == MetricType(metric_type))
        
        if contact_id:
            query = query.filter(Analytics.dimensions["contact_id"].astext == str(contact_id))
        
        if start_date:
            query = query.filter(Analytics.recorded_at >= start_date)
        
        if end_date:
            query = query.filter(Analytics.recorded_at <= end_date)
        
        analytics = query.order_by(Analytics.recorded_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "analytics": [
                {
                    "id": a.id,
                    "metric_type": a.metric_type.value,
                    "metric_name": a.metric_name,
                    "metric_value": a.metric_value,
                    "dimensions": a.dimensions,
                    "recorded_at": a.recorded_at.isoformat()
                }
                for a in analytics
            ],
            "count": len(analytics)
        }
        
    except Exception as e:
        logger.error(f"API: Error getting analytics metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
