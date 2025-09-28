"""
Celery configuration for worker services.
This handles all background task execution and automation processing.
"""
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "automatizaciones",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.automation_tasks",
        "app.tasks.message_tasks",
        "app.tasks.analytics_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.automation_tasks.*": {"queue": "automation"},
        "app.tasks.message_tasks.*": {"queue": "messages"},
        "app.tasks.analytics_tasks.*": {"queue": "analytics"},
    },
    
    # Task execution settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "check-birthday-automations": {
            "task": "app.tasks.automation_tasks.check_birthday_automations",
            "schedule": 60.0,  # Run every minute
        },
        "process-scheduled-automations": {
            "task": "app.tasks.automation_tasks.process_scheduled_automations",
            "schedule": 60.0,  # Run every minute
        },
        "cleanup-old-logs": {
            "task": "app.tasks.analytics_tasks.cleanup_old_logs",
            "schedule": 604800.0,  # Weekly
        },
        "update-analytics": {
            "task": "app.tasks.analytics_tasks.update_system_analytics",
            "schedule": 3600.0,  # Hourly
        },
    },
)

# Optional: Configure task result backend
if settings.ENVIRONMENT == "development":
    celery_app.conf.update(
        result_backend=settings.CELERY_RESULT_BACKEND,
        result_expires=3600,
    )
