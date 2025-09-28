# 🤖 WhatsApp Automation Worker

This is the background worker service for the WhatsApp Automation MVP. It handles all background tasks including automation processing, message handling, and scheduled operations.

## 🏗️ **Architecture**

```
backend-worker/
├── app/                          # Application code
│   ├── core/                    # Core configuration
│   ├── models/                  # Database models
│   ├── services/                # Business logic (worker-specific)
│   └── tasks/                   # Background tasks
├── Dockerfile                   # Worker container
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── requirements.txt            # Python dependencies (worker-only)
├── env.example                 # Environment template
└── README.md                   # This file
```

## 🚀 **Quick Start**

### **Development**
```bash
# Start worker services
docker-compose up -d

# View logs
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Stop services
docker-compose down
```

### **Production**
```bash
# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:port/db"
export REDIS_URL="redis://host:port"
export WHATSAPP_TOKEN="your_token"
# ... other variables

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://host:port
CELERY_BROKER_URL=redis://host:port
CELERY_RESULT_BACKEND=redis://host:port

# Application
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=your_secret_key

# WhatsApp
WHATSAPP_TOKEN=your_whatsapp_token
PHONE_NUMBER_ID=your_phone_number_id
BUSINESS_ID=your_business_id
WEBHOOK_VERIFY_TOKEN=your_webhook_token
```

### **Worker Configuration**
- **Concurrency**: 4 workers (production), 2 workers (development)
- **Memory Limit**: 512MB (production), 256MB (development)
- **CPU Limit**: 0.5 cores (production), 0.25 cores (development)
- **Log Level**: info
- **Restart Policy**: unless-stopped

## 📊 **Background Tasks**

### **Automation Tasks**
- `check_birthday_automations` - Daily birthday processing
- `process_scheduled_automations` - Scheduled task processing
- `process_new_contact_automation` - New contact automation
- `process_message_automation` - Message-based automation
- `execute_automation_for_contact` - Manual execution

### **Message Tasks**
- `process_message_status_update` - Update message status
- `retry_failed_messages` - Retry failed messages

### **Analytics Tasks**
- `update_system_analytics` - Update analytics data
- `cleanup_old_logs` - Cleanup old log data

## 🔄 **Celery Beat Schedule**

```python
beat_schedule = {
    "check-birthday-automations": {
        "task": "app.tasks.automation_tasks.check_birthday_automations",
        "schedule": 60.0,  # Every minute
    },
    "process-scheduled-automations": {
        "task": "app.tasks.automation_tasks.process_scheduled_automations",
        "schedule": 60.0,  # Every minute
    },
    "update-analytics": {
        "task": "app.tasks.analytics_tasks.update_system_analytics",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-old-logs": {
        "task": "app.tasks.analytics_tasks.cleanup_old_logs",
        "schedule": 604800.0,  # Every week
    },
}
```

## 📝 **Logging**

### **Log Files**
```
logs/
├── app.log              # Main application logs
├── errors.log           # Error logs
├── whatsapp.log         # WhatsApp API logs
├── database.log         # Database operations
└── api.log              # API requests
```

### **View Logs**
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# View log files
tail -f logs/app.log
tail -f logs/errors.log
```

## 🐳 **Docker Commands**

### **Development**
```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up --build --force-recreate
```

### **Production**
```bash
# Start production
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production
docker-compose -f docker-compose.prod.yml down
```

## 🔍 **Monitoring**

### **Health Checks**
```bash
# Check worker health
docker-compose exec celery_worker celery -A app.core.celery inspect active

# Check beat health
docker-compose exec celery_beat celery -A app.core.celery inspect scheduled

# Check task statistics
docker-compose exec celery_worker celery -A app.core.celery inspect stats
```

### **Queue Monitoring**
```bash
# Check Redis queues
docker-compose exec redis redis-cli
> KEYS *
> LLEN celery
> LLEN automation
```

## 🚀 **Deployment**

### **Render Deployment**
1. Connect GitHub repository
2. Set environment variables
3. Deploy as background service
4. Configure health checks

### **Docker Deployment**
```bash
# Build production image
docker build -t automatizaciones-worker .

# Run production container
docker run -d \
  --name automatizaciones-worker \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  automatizaciones-worker
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Worker not starting**
   ```bash
   # Check logs
   docker-compose logs celery_worker
   
   # Check environment variables
   docker-compose exec celery_worker env
   ```

2. **Tasks not executing**
   ```bash
   # Check Redis connection
   docker-compose exec redis redis-cli ping
   
   # Check task queue
   docker-compose exec celery_worker celery -A app.core.celery inspect active
   ```

3. **Database connection issues**
   ```bash
   # Check database connection
   docker-compose exec celery_worker python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
   ```

### **Debug Commands**
```bash
# Enter worker container
docker-compose exec celery_worker bash

# Check Python environment
docker-compose exec celery_worker python -c "import sys; print(sys.path)"

# Test database connection
docker-compose exec celery_worker python -c "from app.database import SessionLocal; db = SessionLocal(); print('DB OK')"

# Test Redis connection
docker-compose exec celery_worker python -c "from app.core.celery import celery_app; print(celery_app.control.inspect().active())"
```

## 📚 **API Integration**

This worker service integrates with the main backend API through:

- **Database**: Shared PostgreSQL database
- **Redis**: Shared Redis message broker
- **Logs**: Shared logging system
- **Environment**: Shared environment variables

The worker processes background tasks triggered by:
- API requests from the main backend
- Scheduled tasks via Celery Beat
- Webhook events from WhatsApp
- Manual automation execution

## 🎯 **Performance Optimization**

### **Worker Scaling**
```bash
# Scale workers
docker-compose up --scale celery_worker=3

# Production scaling
docker-compose -f docker-compose.prod.yml up --scale celery_worker=5
```

### **Resource Limits**
- **Memory**: 512MB per worker (production)
- **CPU**: 0.5 cores per worker (production)
- **Concurrency**: 4 tasks per worker (production)

### **Queue Optimization**
- **Priority Queues**: automation, messages, analytics
- **Task Routing**: Component-specific queues
- **Result Backend**: Redis with 1-hour expiration

This worker service provides the background processing power for your WhatsApp Automation MVP! 🚀
