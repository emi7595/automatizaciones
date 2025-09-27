#!/bin/bash

# Railway startup script for Celery Worker
echo "Starting Celery Worker..."

# Install dependencies (if not already installed)
if [ ! -d "venv" ]; then
    python -m venv venv
    source venv/bin/activate
    pip install --break-system-packages -r requirements.txt
else
    source venv/bin/activate
fi

# Start Celery worker
exec celery -A app.core.celery worker --loglevel=info --concurrency=2
