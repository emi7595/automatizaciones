"""
Minimal Celery configuration for backend API to communicate with worker services.
This backend only needs to send tasks to the worker, not execute them.
"""
from celery import Celery
from app.core.config import settings

# Create minimal Celery instance for task queuing only
celery_app = Celery(
    "automatizaciones",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[]  # No tasks included - workers handle all task execution
)

# Minimal Celery configuration for task queuing
celery_app.conf.update(
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing (tasks are sent to worker queues)
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
)

# Note: Beat schedule and task execution are handled by backend-worker/
# This backend only queues tasks for the worker to process
