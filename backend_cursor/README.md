# WhatsApp Automation MVP - Backend

## Architecture Overview

This backend implements a complete WhatsApp automation system with the following components:

### Core Features
- **Contact Management**: Enhanced contact system with metadata, tags, and birthday tracking
- **Message System**: Threaded conversations with comprehensive status tracking
- **Automation Engine**: Flexible trigger-action system with scheduling support
- **Analytics**: Comprehensive metrics and performance tracking
- **User Management**: Role-based authentication and authorization

### Database Schema
- **Users**: Authentication and user management
- **Contacts**: Enhanced contact information with flexible metadata
- **Messages**: Threaded message system with status tracking
- **Automations**: Flexible automation rules with JSON configuration
- **Automation Logs**: Execution tracking and performance monitoring
- **Analytics**: Comprehensive metrics collection

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Docker Development Setup

1. **Clone and navigate to the project:**
```bash
cd backend_cursor
```

2. **Start development environment:**
```bash
docker-compose up -d
```

3. **Set up database schema:**
```bash
# Database schema is automatically applied via docker-compose
# The database_schema.sql file is mounted and executed on PostgreSQL startup
```

4. **Access the application:**
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Manual Setup (Without Docker)

1. **Install Python 3.8+ and PostgreSQL 12+**
2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp env.example .env
# Edit .env with your actual values
```

5. **Set up database:**
```bash
# Create database
createdb automatizaciones

# Apply complete schema
psql -d automatizaciones -f database_schema.sql
```

6. **Run the application:**
```bash
python -m app.main
```

## 📊 Database Schema

### Key Design Decisions

**Birthday Handling:**
- Full date with year: `1990-05-15`
- Unknown year placeholder: `9999-05-15`
- Easy detection with `is_birthday_unknown_year` property

**Message Threading:**
- Auto-generated conversation UUIDs
- Automatic conversation creation on first message
- Threaded message history

**Flexible JSON Fields:**
- `trigger_conditions`: Complex automation triggers
- `action_payload`: Flexible action configuration
- `metadata`: Extensible message metadata
- `dimensions`: Analytics filtering

**Status Tracking:**
- Message flow: `pending → sent → delivered → read`
- Error handling with detailed error messages
- Comprehensive execution logging

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Source |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | **Auto-provided by Render** |
| `WHATSAPP_TOKEN` | WhatsApp Cloud API access token | Yes | Manual configuration |
| `PHONE_NUMBER_ID` | WhatsApp phone number ID | Yes | Manual configuration |
| `BUSINESS_ID` | WhatsApp business ID | Yes | Manual configuration |
| `WEBHOOK_VERIFY_TOKEN` | Webhook verification token | Yes | Manual configuration |
| `SECRET_KEY` | JWT secret key | Yes | Manual configuration |
| `ALLOWED_ORIGINS` | CORS allowed origins | Yes | Manual configuration |

**Note**: `DATABASE_URL` is automatically provided by Render when you add a PostgreSQL service. You don't need to configure it manually!

### Database Indexes

The schema includes optimized indexes for:
- Contact lookups (phone, email, birthday)
- Message queries (contact, conversation, status)
- Automation filtering (trigger type, active status)
- Analytics queries (metric type, time ranges)

## 🏛️ Project Structure

```
backend_cursor/
├── app/
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── celery.py          # Celery background tasks
│   ├── models/
│   │   ├── user.py           # User authentication
│   │   ├── contact.py        # Enhanced contacts
│   │   ├── message.py        # Threaded messages
│   │   ├── automation.py     # Automation rules
│   │   ├── automation_log.py # Execution logs
│   │   └── analytics.py      # Metrics tracking
│   ├── tasks/                # Background task modules
│   │   ├── automation_tasks.py
│   │   ├── message_tasks.py
│   │   └── analytics_tasks.py
│   ├── database.py           # Database configuration
│   └── main.py              # FastAPI application
├── database_schema.sql       # Complete SQL schema
├── Dockerfile               # Multi-stage production image
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── .dockerignore           # Docker ignore patterns
├── requirements.txt         # Python dependencies
├── database_schema.sql     # Complete SQL schema
├── env.example             # Environment template
├── DOCKER.md               # Docker documentation
└── README.md               # This file
```

## 🔄 Database Schema Management

### Manual Schema Setup

```bash
# Apply complete schema (recommended)
psql -d automatizaciones -f database_schema.sql

# Or use Docker Compose (automatic)
docker-compose up -d
```

### Schema Updates

```bash
# For schema changes, manually run SQL commands
psql -d automatizaciones -c "ALTER TABLE contacts ADD COLUMN new_field VARCHAR(100);"

# Or create new SQL files for specific changes
psql -d automatizaciones -f schema_update_v2.sql
```

## 📈 Performance Considerations

### Indexing Strategy
- Primary keys and foreign keys are automatically indexed
- JSON fields use GIN indexes for efficient querying
- Time-based queries have dedicated indexes
- Composite indexes for common query patterns

### Scalability Features
- Connection pooling with SQLAlchemy
- Efficient JSON querying with PostgreSQL
- Partitioning-ready schema design
- Background task processing with Celery

## 🔒 Security Features

- Role-based access control (Admin/User)
- JWT token authentication
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration for frontend integration

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app
```

## 🚀 Deployment

### Render Deployment

**Step 1: Create PostgreSQL Service**
1. In Render dashboard, create a new PostgreSQL service
2. Render automatically provides `DATABASE_URL` environment variable
3. No manual database configuration needed!

**Step 2: Deploy Backend Service**
1. Connect GitHub repository to Render
2. Set environment variables (except `DATABASE_URL` - it's automatic):
   - `WHATSAPP_TOKEN`
   - `PHONE_NUMBER_ID` 
   - `BUSINESS_ID`
   - `WEBHOOK_VERIFY_TOKEN`
   - `SECRET_KEY`
   - `ALLOWED_ORIGINS`
3. Deploy automatically on push to main branch
4. Database schema is applied automatically via `database_schema.sql`

**Step 3: Verify Deployment**
- Check Render logs for successful database connection
- Verify API endpoints at `https://your-app.onrender.com`
- Check database schema with `psql` commands

### Local Development
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔮 Future Enhancements

- WhatsApp template message support
- Advanced automation workflows
- Real-time message status updates
- Comprehensive analytics dashboard
- Multi-language support
- Integration with external CRMs

---

**Phase 1 Complete**: Database schema and models are ready for WhatsApp integration and automation engine implementation.
