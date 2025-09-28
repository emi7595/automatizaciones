# 🚀 WhatsApp Automation Backend API

This is the main backend API service for the WhatsApp Automation MVP. It handles HTTP requests, WhatsApp integration, and API endpoints.

## 🏗️ **Architecture**

```
backend/
├── app/                          # Application code
│   ├── core/                    # Core configuration
│   ├── models/                  # Database models
│   ├── services/                # Business logic
│   ├── api/                     # API endpoints
│   └── schemas/                 # Data schemas
├── Dockerfile                   # API container
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── requirements.txt            # Python dependencies
├── env.example                 # Environment template
└── README.md                   # This file
```

## 🚀 **Quick Start**

### **Development**
```bash
# Start backend services (API + Database + Redis)
docker-compose up -d

# Start worker services (in separate terminal)
cd ../backend-worker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
cd ../backend-worker
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

# CORS
ALLOWED_ORIGINS=https://your-frontend-url.com
```

## 🌐 **API Endpoints**

### **Message API**
- `POST /api/messages/send` - Send WhatsApp message
- `POST /api/messages/send-template` - Send template message
- `GET /api/messages/` - List messages
- `GET /api/messages/{id}` - Get specific message
- `GET /api/messages/conversations/` - List conversations
- `GET /api/messages/conversations/{id}` - Get conversation messages

### **Webhook API**
- `GET /webhooks/whatsapp` - Webhook verification
- `POST /webhooks/whatsapp` - Receive WhatsApp webhooks
- `POST /webhooks/whatsapp/test` - Test webhook

### **Automation API**
- `POST /api/automations/` - Create automation
- `GET /api/automations/` - List automations
- `GET /api/automations/{id}` - Get automation
- `PUT /api/automations/{id}` - Update automation
- `DELETE /api/automations/{id}` - Delete automation
- `POST /api/automations/{id}/execute` - Execute automation
- `GET /api/automations/stats/overview` - Get statistics

## 📊 **Logging**

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
docker-compose logs -f backend

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

## 🔍 **Health Checks**

### **API Health**
```bash
# Check API health
curl http://localhost:8000/health

# Check API docs
curl http://localhost:8000/docs
```

### **Database Health**
```bash
# Check database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
```

### **Redis Health**
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping
```

## 🚀 **Deployment**

### **Render Deployment**
1. Connect GitHub repository
2. Set environment variables
3. Deploy as web service
4. Configure health checks

### **Docker Deployment**
```bash
# Build production image
docker build -t automatizaciones-backend .

# Run production container
docker run -d \
  --name automatizaciones-backend \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  automatizaciones-backend
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **API not starting**
   ```bash
   # Check logs
   docker-compose logs backend
   
   # Check environment variables
   docker-compose exec backend env
   ```

2. **Database connection issues**
   ```bash
   # Check database connection
   docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
   ```

3. **WhatsApp integration issues**
   ```bash
   # Check WhatsApp configuration
   docker-compose exec backend python -c "from app.core.config import settings; print(f'Token: {bool(settings.WHATSAPP_TOKEN)}')"
   ```

### **Debug Commands**
```bash
# Enter backend container
docker-compose exec backend bash

# Check Python environment
docker-compose exec backend python -c "import sys; print(sys.path)"

# Test database connection
docker-compose exec backend python -c "from app.database import SessionLocal; db = SessionLocal(); print('DB OK')"

# Test WhatsApp service
docker-compose exec backend python -c "from app.services.whatsapp_service import whatsapp_service; print('WhatsApp OK')"
```

## 📚 **Worker Integration**

This backend API integrates with the worker service through:

- **Database**: Shared PostgreSQL database
- **Redis**: Shared Redis message broker
- **Logs**: Shared logging system
- **Environment**: Shared environment variables

The worker service processes background tasks triggered by:
- API requests from this backend
- Scheduled tasks via Celery Beat
- Webhook events from WhatsApp
- Manual automation execution

## 🎯 **Performance Optimization**

### **API Scaling**
```bash
# Scale API instances
docker-compose up --scale backend=3

# Production scaling
docker-compose -f docker-compose.prod.yml up --scale backend=5
```

### **Resource Limits**
- **Memory**: 512MB per instance (production)
- **CPU**: 0.5 cores per instance (production)
- **Connections**: 100 concurrent requests

### **Database Optimization**
- **Connection Pooling**: 20 connections
- **Query Optimization**: Indexed tables
- **Result Caching**: Redis-based caching

This backend API provides the HTTP interface for your WhatsApp Automation MVP! 🚀