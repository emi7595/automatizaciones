#!/bin/bash

# Railway startup script for WhatsApp Automation Backend
echo "Starting WhatsApp Automation Backend..."

# Install dependencies (if not already installed)
if [ ! -d "venv" ]; then
    python -m venv venv
    source venv/bin/activate
    pip install --break-system-packages -r requirements.txt
else
    source venv/bin/activate
fi

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
