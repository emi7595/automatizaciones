# 🏗️ WhatsApp Automation MVP - Architecture Diagram

## 📋 **Complete System Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    WHATSAPP AUTOMATION MVP                                      │
│                                    Complete Architecture Flow                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 **Phase Overview**

```
Phase 1: Database & Models ──► Phase 2: WhatsApp Integration ──► Phase 3: Automation Engine
     ✅ COMPLETE                    ✅ COMPLETE                      ✅ COMPLETE
```

---

## 📁 **File Structure & Connections**

```
backend/
├── app/
│   ├── main.py                           # 🚀 FastAPI Application Entry Point
│   │   ├── CORS Middleware
│   │   ├── Error Handlers
│   │   ├── Health Check
│   │   └── Router Registration
│   │
│   ├── core/
│   │   ├── config.py                     # ⚙️ Configuration Management
│   │   │   ├── Environment Variables
│   │   │   ├── Database Settings
│   │   │   ├── WhatsApp Settings
│   │   │   └── Redis/Celery Settings
│   │   │
│   │   ├── logging.py                    # 📊 Comprehensive Logging System
│   │   │   ├── Colored Console Output
│   │   │   ├── File-based Logging
│   │   │   ├── Performance Monitoring
│   │   │   └── Component-specific Logs
│   │   │
│   │   └── celery.py                     # 🔄 Background Task Configuration
│   │       ├── Celery App Setup
│   │       ├── Task Routing
│   │       ├── Beat Schedule
│   │       └── Queue Management
│   │
│   ├── database.py                       # 🗄️ Database Connection & ORM
│   │   ├── SQLAlchemy Engine
│   │   ├── Session Management
│   │   ├── Table Creation
│   │   └── Connection Pooling
│   │
│   ├── models/                          # 📊 Database Models (Phase 1)
│   │   ├── user.py                      # 👤 User Management
│   │   ├── contact.py                   # 📞 Contact Information
│   │   ├── message.py                   # 💬 Message Threading
│   │   ├── automation.py                # 🤖 Automation Rules
│   │   ├── automation_log.py            # 📝 Execution Logs
│   │   └── analytics.py                  # 📈 System Analytics
│   │
│   ├── schemas/                         # 🔍 Pydantic Models
│   │   ├── message.py                   # Message API Schemas
│   │   └── automation.py                # Automation API Schemas
│   │
│   ├── services/                        # 🏢 Business Logic Layer
│   │   ├── whatsapp_service.py         # 📱 WhatsApp Cloud API (Phase 2)
│   │   │   ├── Send Messages
│   │   │   ├── Template Messages
│   │   │   ├── Webhook Processing
│   │   │   └── Status Updates
│   │   │
│   │   ├── message_service.py          # 💬 Message Management (Phase 2)
│   │   │   ├── Send Messages
│   │   │   ├── Conversation Management
│   │   │   ├── Message Threading
│   │   │   └── Automation Triggers
│   │   │
│   │   ├── automation_service.py       # 🤖 Automation CRUD (Phase 3)
│   │   │   ├── Create/Read/Update/Delete
│   │   │   ├── Validation Logic
│   │   │   ├── Manual Execution
│   │   │   └── Statistics
│   │   │
│   │   └── automation_engine.py        # ⚙️ Automation Engine (Phase 3)
│   │       ├── Trigger Processing
│   │       ├── Action Execution
│   │       ├── Condition Evaluation
│   │       └── Error Handling
│   │
│   ├── api/                            # 🌐 API Endpoints
│   │   ├── messages.py                 # Message API (Phase 2)
│   │   │   ├── POST /send
│   │   │   ├── GET /conversations
│   │   │   ├── GET /messages
│   │   │   └── PUT /status
│   │   │
│   │   ├── webhooks.py                 # Webhook API (Phase 2)
│   │   │   ├── GET /whatsapp (verify)
│   │   │   ├── POST /whatsapp (receive)
│   │   │   └── POST /whatsapp/test
│   │   │
│   │   └── automations.py              # Automation API (Phase 3)
│   │       ├── CRUD Operations
│   │       ├── Manual Execution
│   │       ├── Statistics
│   │       └── Examples
│   │
│   └── tasks/                          # 🔄 Background Tasks
│       ├── message_tasks.py            # Message Processing (Phase 2)
│       │   ├── Status Updates
│       │   ├── Retry Logic
│       │   └── Error Handling
│       │
│       ├── automation_tasks.py        # Automation Processing (Phase 3)
│       │   ├── Birthday Triggers
│       │   ├── Scheduled Tasks
│       │   ├── Message Triggers
│       │   └── New Contact Triggers
│       │
│       └── analytics_tasks.py         # Analytics Processing
│           ├── Data Aggregation
│           ├── Report Generation
│           └── Cleanup Tasks
│
├── database_schema.sql                 # 🗄️ Complete Database Schema
├── docker-compose.yml                  # 🐳 Development Environment
├── docker-compose.prod.yml            # 🚀 Production Environment
├── Dockerfile                         # 📦 Container Configuration
├── requirements.txt                   # 📋 Python Dependencies
├── env.example                        # 🔧 Environment Template
└── logs/                              # 📊 Log Files
    ├── app.log                        # Main Application Logs
    ├── errors.log                     # Error Logs
    ├── whatsapp.log                   # WhatsApp API Logs
    ├── database.log                   # Database Operations
    └── api.log                        # API Request Logs
```

---

## 🔄 **Complete Process Flow**

### **1. Application Startup**
```
main.py
├── setup_logging()                    # Initialize logging system
├── create_tables()                    # Create database tables
├── include_router(messages)           # Register message API
├── include_router(webhooks)           # Register webhook API
├── include_router(automations)        # Register automation API
└── Start FastAPI Server
```

### **2. WhatsApp Message Flow**
```
📱 WhatsApp User ──► Meta Webhook ──► webhooks.py
                                        ├── verify_webhook()
                                        └── receive_webhook()
                                            └── message_service.py
                                                ├── process_incoming_message()
                                                ├── Create Message Record
                                                └── Trigger Automation
                                                    └── automation_tasks.py
                                                        └── process_message_automation()
                                                            └── automation_engine.py
                                                                ├── process_message_trigger()
                                                                ├── process_keyword_trigger()
                                                                └── execute_automation_for_contact()
```

### **3. Automation Execution Flow**
```
🤖 Automation Trigger ──► automation_engine.py
                            ├── process_new_contact_trigger()
                            ├── process_birthday_trigger()
                            ├── process_message_trigger()
                            ├── process_keyword_trigger()
                            └── process_scheduled_automations()
                                └── _execute_automation_for_contact()
                                    ├── _execute_send_message_action()
                                    ├── _execute_update_contact_action()
                                    └── _execute_log_activity_action()
```

### **4. Background Task Processing**
```
⏰ Celery Beat Scheduler ──► automation_tasks.py
                            ├── check_birthday_automations()     # Every minute
                            ├── process_scheduled_automations()  # Every minute
                            ├── process_new_contact_automation() # On new contact
                            └── process_message_automation()    # On new message
```

### **5. API Request Flow**
```
🌐 API Request ──► FastAPI Router ──► Service Layer ──► Database ──► Response
    │                    │                │              │
    ├── /api/messages    ├── messages.py  ├── message_service.py
    ├── /api/automations ├── automations.py ├── automation_service.py
    └── /webhooks        └── webhooks.py  └── whatsapp_service.py
```

---

## 🔗 **File Dependencies & Connections**

### **Core Dependencies**
```
main.py
├── core/config.py          # Settings and configuration
├── core/logging.py         # Logging system
├── database.py             # Database connection
├── api/messages.py         # Message endpoints
├── api/webhooks.py         # Webhook endpoints
└── api/automations.py      # Automation endpoints
```

### **Service Layer Dependencies**
```
services/
├── whatsapp_service.py
│   ├── core/config.py      # WhatsApp settings
│   ├── core/logging.py     # Logging
│   └── httpx              # HTTP client
│
├── message_service.py
│   ├── models/message.py   # Message model
│   ├── models/contact.py   # Contact model
│   ├── services/whatsapp_service.py
│   └── tasks/automation_tasks.py
│
├── automation_service.py
│   ├── models/automation.py
│   ├── models/automation_log.py
│   └── core/logging.py
│
└── automation_engine.py
    ├── models/automation.py
    ├── models/contact.py
    ├── models/message.py
    └── services/automation_service.py
```

### **API Layer Dependencies**
```
api/
├── messages.py
│   ├── schemas/message.py
│   ├── services/message_service.py
│   └── database.py
│
├── webhooks.py
│   ├── services/whatsapp_service.py
│   ├── services/message_service.py
│   └── database.py
│
└── automations.py
    ├── schemas/automation.py
    ├── services/automation_service.py
    └── database.py
```

### **Task Layer Dependencies**
```
tasks/
├── message_tasks.py
│   ├── models/message.py
│   ├── core/celery.py
│   └── core/logging.py
│
├── automation_tasks.py
│   ├── models/automation.py
│   ├── models/contact.py
│   ├── services/automation_engine.py
│   └── core/celery.py
│
└── analytics_tasks.py
    ├── models/analytics.py
    └── core/celery.py
```

---

## 🎯 **Data Flow Architecture**

### **Incoming Message Flow**
```
📱 WhatsApp ──► Meta Webhook ──► webhooks.py ──► message_service.py
                                                      ├── Create Message Record
                                                      ├── Update Contact
                                                      └── Trigger Automation
                                                          └── automation_engine.py
                                                              ├── Check Triggers
                                                              ├── Execute Actions
                                                              └── Log Results
```

### **Outgoing Message Flow**
```
🌐 API Request ──► messages.py ──► message_service.py ──► whatsapp_service.py
                                                              ├── WhatsApp API Call
                                                              ├── Create Message Record
                                                              └── Update Status
```

### **Automation Flow**
```
⏰ Trigger Event ──► automation_engine.py ──► Action Execution
                        ├── New Contact ──► Send Welcome Message
                        ├── Birthday ──► Send Birthday Greeting
                        ├── Keyword ──► Send Response
                        └── Scheduled ──► Execute Task
```

---

## 🔄 **Background Task Architecture**

### **Celery Beat Schedule**
```
⏰ Every Minute:
├── check_birthday_automations()     # Check for birthdays
└── process_scheduled_automations()  # Check scheduled tasks

⏰ Every Hour:
└── update_system_analytics()        # Update analytics

⏰ Every Week:
└── cleanup_old_logs()               # Cleanup old data
```

### **Event-Driven Tasks**
```
📨 New Message ──► process_message_automation()
👤 New Contact ──► process_new_contact_automation()
📞 Manual Execution ──► execute_automation_for_contact()
```

---

## 📊 **Logging Architecture**

### **Log File Structure**
```
logs/
├── app.log              # Main application logs
├── errors.log           # Error logs only
├── whatsapp.log         # WhatsApp API interactions
├── database.log         # Database operations
└── api.log              # API requests/responses
```

### **Logging Flow**
```
Application Code ──► core/logging.py ──► Multiple Log Files
                        ├── Console Output (colored)
                        ├── File Rotation (10MB, 5 files)
                        └── Component-specific Logs
```

---

## 🐳 **Docker Architecture**

### **Development Environment**
```
docker-compose.yml
├── postgres:5432        # Database
├── redis:6379           # Message broker
├── backend:8000         # FastAPI application
├── celery_worker        # Background tasks
└── celery_beat          # Scheduled tasks
```

### **Production Environment**
```
docker-compose.prod.yml
├── postgres:5432        # Production database
├── redis:6379           # Production Redis
├── backend:8000         # Production FastAPI
├── celery_worker        # Production workers
└── celery_beat          # Production scheduler
```

---

## 🎯 **Complete System Integration**

### **Phase 1 → Phase 2 → Phase 3 Integration**
```
Phase 1 (Database) ──► Phase 2 (WhatsApp) ──► Phase 3 (Automation)
     │                        │                        │
     ├── Models              ├── Message Service      ├── Automation Engine
     ├── Database            ├── WhatsApp Service     ├── Automation Service
     └── Schemas            └── Webhook Processing    └── Background Tasks
```

### **End-to-End Process**
```
1. 📱 WhatsApp Message Received
   └── webhooks.py → message_service.py → automation_engine.py

2. 🤖 Automation Triggered
   └── automation_engine.py → whatsapp_service.py → WhatsApp API

3. 📊 Results Logged
   └── automation_log.py → analytics.py → logging system

4. 🔄 Background Processing
   └── celery_tasks.py → automation_engine.py → database updates
```

---

## 🚀 **Deployment Architecture**

### **Render Deployment**
```
GitHub Push ──► GitHub Actions ──► Render Services
    │                │                    │
    ├── Backend      ├── Build & Deploy  ├── Backend Service
    ├── Frontend     └── Environment     ├── Database Service
    └── Database         Variables       └── Redis Service
```

### **Environment Variables**
```
DATABASE_URL          # PostgreSQL connection
REDIS_URL            # Redis connection
WHATSAPP_TOKEN       # WhatsApp API token
PHONE_NUMBER_ID      # WhatsApp phone number
BUSINESS_ID          # WhatsApp business ID
WEBHOOK_VERIFY_TOKEN # Webhook verification
SECRET_KEY           # Application secret
```

---

## 🎉 **Complete System Overview**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    WHATSAPP AUTOMATION MVP                                      │
│                                                                                                 │
│  📱 WhatsApp ──► 🌐 API ──► 🗄️ Database ──► 🤖 Automation ──► 📱 WhatsApp                    │
│                                                                                                 │
│  Phase 1: Database & Models ✅                                                                 │
│  Phase 2: WhatsApp Integration ✅                                                               │
│  Phase 3: Automation Engine ✅                                                                  │
│                                                                                                 │
│  🚀 Ready for Production!                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

This architecture provides a complete, scalable, and maintainable WhatsApp automation system with comprehensive logging, error handling, and real-time processing capabilities.
