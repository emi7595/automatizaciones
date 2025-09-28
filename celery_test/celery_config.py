"""
Minimal Celery configuration for testing Railway worker.
"""
import os
from celery import Celery

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Create minimal Celery instance
celery_app = Celery(
    "test_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["celery_test.test_tasks"]
)

# Minimal configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=1,  # Single worker for testing
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

print(f"🔧 Celery broker URL: {CELERY_BROKER_URL}")
print(f"🔧 Celery result backend: {CELERY_RESULT_BACKEND}")
print("🚀 Minimal Celery configuration loaded")
