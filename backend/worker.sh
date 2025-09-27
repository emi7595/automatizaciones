#!/bin/bash

# Railway startup script for Celery Worker
echo "Starting Celery Worker..."

# Install dependencies
pip install -r requirements.txt

# Start Celery worker
exec celery -A app.core.celery worker --loglevel=info --concurrency=2
