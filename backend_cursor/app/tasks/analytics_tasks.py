"""
Analytics background tasks for metrics collection and cleanup.
"""
from celery import current_task
from app.core.celery import celery_app
from app.database import SessionLocal
from app.models.analytics import Analytics, MetricType
from app.models.automation_log import AutomationLog
from app.models.contact import Contact
from app.models.message import Message
from app.models.automation import Automation
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def update_system_analytics(self):
    """
    Update system-wide analytics metrics.
    """
    db = SessionLocal()
    try:
        # Get current metrics
        total_contacts = db.query(Contact).count()
        active_contacts = db.query(Contact).filter(Contact.is_active == True).count()
        total_automations = db.query(Automation).count()
        active_automations = db.query(Automation).filter(Automation.is_active == True).count()
        total_messages = db.query(Message).count()
        
        # Update analytics records
        metrics_to_update = [
            ("total_contacts", total_contacts, MetricType.SYSTEM_PERFORMANCE),
            ("active_contacts", active_contacts, MetricType.SYSTEM_PERFORMANCE),
            ("total_automations", total_automations, MetricType.SYSTEM_PERFORMANCE),
            ("active_automations", active_automations, MetricType.SYSTEM_PERFORMANCE),
            ("total_messages", total_messages, MetricType.SYSTEM_PERFORMANCE),
        ]
        
        for metric_name, metric_value, metric_type in metrics_to_update:
            # Check if metric already exists for today
            today = datetime.now().date()
            existing_metric = db.query(Analytics).filter(
                Analytics.metric_name == metric_name,
                Analytics.recorded_at >= today,
                Analytics.recorded_at < today + timedelta(days=1)
            ).first()
            
            if existing_metric:
                # Update existing metric
                existing_metric.metric_value = metric_value
            else:
                # Create new metric
                new_metric = Analytics(
                    metric_type=metric_type,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    dimensions={"period": "daily"}
                )
                db.add(new_metric)
        
        db.commit()
        
        return {
            "status": "completed",
            "metrics_updated": len(metrics_to_update),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating system analytics: {str(e)}")
        db.rollback()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def cleanup_old_logs(self, days_to_keep: int = 30):
    """
    Clean up old automation logs and analytics data.
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean up old automation logs
        old_logs = db.query(AutomationLog).filter(
            AutomationLog.executed_at < cutoff_date
        ).all()
        
        logs_deleted = 0
        for log in old_logs:
            db.delete(log)
            logs_deleted += 1
        
        # Clean up old analytics (keep only daily summaries)
        old_analytics = db.query(Analytics).filter(
            Analytics.recorded_at < cutoff_date,
            Analytics.dimensions["period"] != "daily"
        ).all()
        
        analytics_deleted = 0
        for analytic in old_analytics:
            db.delete(analytic)
            analytics_deleted += 1
        
        db.commit()
        
        return {
            "status": "completed",
            "logs_deleted": logs_deleted,
            "analytics_deleted": analytics_deleted,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old logs: {str(e)}")
        db.rollback()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def calculate_automation_performance(self, automation_id: int):
    """
    Calculate performance metrics for a specific automation.
    """
    db = SessionLocal()
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            return {"status": "failed", "error": "Automation not found"}
        
        # Get logs from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        logs = db.query(AutomationLog).filter(
            AutomationLog.automation_id == automation_id,
            AutomationLog.executed_at >= thirty_days_ago
        ).all()
        
        # Calculate metrics
        total_executions = len(logs)
        successful_executions = len([log for log in logs if log.execution_status == "success"])
        failed_executions = len([log for log in logs if log.execution_status == "failed"])
        total_contacts_affected = sum(log.contacts_affected for log in logs)
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Store performance metrics
        performance_metric = Analytics(
            metric_type=MetricType.AUTOMATION_PERFORMANCE,
            metric_name=f"automation_{automation_id}_performance",
            metric_value=success_rate,
            dimensions={
                "automation_id": automation_id,
                "automation_name": automation.name,
                "period": "30_days"
            }
        )
        db.add(performance_metric)
        db.commit()
        
        return {
            "status": "completed",
            "automation_id": automation_id,
            "total_executions": total_executions,
            "success_rate": success_rate,
            "total_contacts_affected": total_contacts_affected
        }
        
    except Exception as e:
        logger.error(f"Error calculating automation performance: {str(e)}")
        db.rollback()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
