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
    
    # Worker concurrency and memory management
    worker_concurrency=4,  # Reduced from default 48 to 4 workers
    worker_max_memory_per_child=200000,  # 200MB per worker process
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
    
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
    
    # Memory optimization
    task_compression="gzip",  # Compress task data
    result_compression="gzip",  # Compress result data
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Beat schedule for periodic tasks (optimized for memory usage)
    beat_schedule={
        "check-birthday-automations": {
            "task": "app.tasks.automation_tasks.check_birthday_automations",
            "schedule": 300.0,  # Run every 5 minutes (reduced frequency)
        },
        "process-scheduled-automations": {
            "task": "app.tasks.automation_tasks.process_scheduled_automations",
            "schedule": 300.0,  # Run every 5 minutes (reduced frequency)
        },
        "cleanup-old-logs": {
            "task": "app.tasks.analytics_tasks.cleanup_old_logs",
            "schedule": 604800.0,  # Weekly
        },
        "update-analytics": {
            "task": "app.tasks.analytics_tasks.update_system_analytics",
            "schedule": 7200.0,  # Every 2 hours (reduced frequency)
        },
    },
)

# Environment-specific optimizations
if settings.ENVIRONMENT == "development":
    # Development: More conservative settings
    celery_app.conf.update(
        worker_concurrency=2,  # Even fewer workers in development
        worker_max_memory_per_child=100000,  # 100MB per worker
        result_backend=settings.CELERY_RESULT_BACKEND,
        result_expires=3600,
    )
elif settings.ENVIRONMENT == "production":
    # Production: Optimized for production workloads
    celery_app.conf.update(
        worker_concurrency=6,  # Slightly more workers for production
        worker_max_memory_per_child=300000,  # 300MB per worker
        worker_max_tasks_per_child=100,  # More tasks before restart
    )

# Debug: Log configuration on startup
import logging
logger = logging.getLogger(__name__)
logger.info(f"🔧 Celery broker URL: {settings.CELERY_BROKER_URL}")
logger.info(f"🔧 Celery result backend: {settings.CELERY_RESULT_BACKEND}")
logger.info(f"🔧 Backend API URL: {settings.BACKEND_API_URL}")
logger.info(f"🔧 Environment: {settings.ENVIRONMENT}")
