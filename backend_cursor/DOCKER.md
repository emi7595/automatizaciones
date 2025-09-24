# Docker Architecture - WhatsApp Automation MVP

This document describes the Docker architecture and deployment strategy for the WhatsApp Automation MVP.

## 🐳 Docker Architecture Overview

The application is designed to run in a containerized environment with the following services:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI      │    │   PostgreSQL   │    │     Redis      │
│   Backend      │◄──►│   Database     │    │   Background   │
│   (Port 8000)  │    │   (Port 5432)  │    │   Tasks       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Celery        │    │   Celery        │    │   WhatsApp      │
│   Worker        │    │   Beat          │    │   Cloud API     │
│   (Background)   │    │   (Scheduler)    │    │   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Docker Files Structure

```
backend_cursor/
├── Dockerfile                 # Multi-stage production image
├── docker-compose.yml         # Development environment
├── docker-compose.prod.yml    # Production environment
├── .dockerignore             # Docker ignore patterns
├── scripts/
│   ├── dev.sh                # Development startup script
│   ├── prod.sh               # Production deployment script
│   └── migrate.sh            # Database migration script
└── app/
    ├── core/
    │   └── celery.py          # Celery configuration
    └── tasks/                 # Background task modules
```

## 🏗️ Multi-Stage Dockerfile

The Dockerfile uses a multi-stage build for optimized production images:

### Stage 1: Builder
- Installs build dependencies
- Creates virtual environment
- Installs Python packages

### Stage 2: Production
- Copies virtual environment from builder
- Creates non-root user for security
- Sets up application code
- Configures health checks

### Key Features:
- **Security**: Non-root user execution
- **Optimization**: Multi-stage build reduces image size
- **Health Checks**: Built-in container health monitoring
- **Production Ready**: Gunicorn WSGI server

## 🚀 Development Environment

### Quick Start

```bash
# Start development environment
./scripts/dev.sh

# Or manually
docker-compose up -d
```

### Development Services

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | FastAPI application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Background tasks |
| Celery Worker | - | Background processing |
| Celery Beat | - | Scheduled tasks |

### Development Features

- **Hot Reload**: Code changes trigger automatic restarts
- **Volume Mounting**: Source code mounted for development
- **Health Checks**: Automatic service health monitoring
- **Log Aggregation**: Centralized logging with docker-compose

## 🏭 Production Environment

### Production Deployment

```bash
# Deploy to production
./scripts/prod.sh

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### Production Optimizations

- **Resource Limits**: Memory and CPU constraints
- **Security**: Non-root user execution
- **Scalability**: Horizontal scaling support
- **Monitoring**: Health checks and logging
- **Persistence**: Named volumes for data

### Production Services

| Service | Resources | Description |
|---------|-----------|-------------|
| Backend API | 512M RAM | FastAPI with Gunicorn |
| PostgreSQL | 1G RAM | Production database |
| Redis | 256M RAM | Background task queue |
| Celery Worker | 256M RAM | Background processing |
| Celery Beat | 128M RAM | Task scheduler |

## 🔧 Configuration Management

### Environment Variables

All configuration is managed through environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/automatizaciones

# Redis
REDIS_URL=redis://redis:6379
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379

# WhatsApp API
WHATSAPP_TOKEN=your_token
PHONE_NUMBER_ID=your_phone_id
BUSINESS_ID=your_business_id
WEBHOOK_VERIFY_TOKEN=your_webhook_token

# Security
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
```

### Configuration Files

- **Development**: `docker-compose.yml`
- **Production**: `docker-compose.prod.yml`
- **Environment**: `.env` (created from `env.example`)

## 📊 Background Tasks Architecture

### Celery Configuration

```python
# Task Queues
automation_queue    # Automation processing
messages_queue      # Message handling
analytics_queue     # Metrics collection
```

### Scheduled Tasks

- **Daily**: Birthday automation checks
- **Hourly**: System analytics updates
- **Weekly**: Log cleanup and maintenance

### Task Types

1. **Automation Tasks**
   - Birthday automation processing
   - Contact trigger execution
   - Automation performance tracking

2. **Message Tasks**
   - WhatsApp message sending
   - Status updates
   - Retry failed messages

3. **Analytics Tasks**
   - System metrics collection
   - Performance monitoring
   - Data cleanup

## 🗄️ Database Management

### Migration Strategy

```bash
# Run migrations
./scripts/migrate.sh

# Or manually
docker-compose exec backend alembic upgrade head
```

### Database Features

- **PostgreSQL 15**: Latest stable version
- **Alembic Migrations**: Version-controlled schema changes
- **Health Checks**: Connection monitoring
- **Backup Ready**: Volume persistence

### Database Schema

- **6 Tables**: Users, Contacts, Messages, Automations, Logs, Analytics
- **Optimized Indexes**: Performance-optimized queries
- **JSON Fields**: Flexible configuration storage
- **Foreign Keys**: Data integrity constraints

## 🔍 Monitoring and Logging

### Health Checks

```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Logging Strategy

- **Application Logs**: FastAPI and Celery logs
- **Database Logs**: PostgreSQL query logs
- **System Logs**: Container and service logs
- **Error Tracking**: Comprehensive error logging

### Monitoring Endpoints

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`
- **Metrics**: Built-in analytics collection

## 🚀 Deployment Strategies

### Development Deployment

```bash
# Start all services
./scripts/dev.sh

# Access services
curl http://localhost:8000/health
```

### Production Deployment

```bash
# Deploy to production
./scripts/prod.sh

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```

### Cloud Deployment

The architecture is ready for cloud deployment on:
- **Render**: Direct Docker deployment
- **AWS ECS**: Container orchestration
- **Google Cloud Run**: Serverless containers
- **Azure Container Instances**: Managed containers

## 🔒 Security Considerations

### Container Security

- **Non-root User**: All containers run as non-root
- **Resource Limits**: Memory and CPU constraints
- **Network Isolation**: Internal Docker networks
- **Secret Management**: Environment variable security

### Application Security

- **JWT Authentication**: Secure API access
- **CORS Configuration**: Frontend integration
- **Input Validation**: Pydantic schema validation
- **SQL Injection Prevention**: SQLAlchemy ORM

## 📈 Performance Optimization

### Database Optimization

- **Connection Pooling**: SQLAlchemy connection management
- **Index Strategy**: Optimized database indexes
- **Query Optimization**: Efficient ORM queries
- **Caching**: Redis-based caching

### Application Optimization

- **Async Processing**: Celery background tasks
- **Resource Management**: Memory and CPU optimization
- **Load Balancing**: Horizontal scaling support
- **Monitoring**: Performance metrics collection

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   docker-compose exec postgres pg_isready -U automatizaciones_user
   ```

2. **Redis Connection Issues**
   ```bash
   docker-compose exec redis redis-cli ping
   ```

3. **Service Health Issues**
   ```bash
   docker-compose ps
   docker-compose logs [service_name]
   ```

### Debug Commands

```bash
# Access database
docker-compose exec postgres psql -U automatizaciones_user -d automatizaciones

# Access Redis
docker-compose exec redis redis-cli

# View service logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart [service_name]
```

## 🎯 Next Steps

The Docker architecture is ready for:
- **Phase 2**: WhatsApp Cloud API integration
- **Phase 3**: Automation engine implementation
- **Phase 4**: API endpoints development
- **Phase 5**: Frontend integration

All services are containerized and ready for production deployment!
