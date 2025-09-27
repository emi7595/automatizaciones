#!/bin/sh
celery -A app.core.celery worker --loglevel=info --concurrency=1 &
python -m http.server $PORT