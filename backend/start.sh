#!/bin/bash

# Railway startup script for WhatsApp Automation Backend
echo "Starting WhatsApp Automation Backend..."

# Install dependencies
pip install -r requirements.txt

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
