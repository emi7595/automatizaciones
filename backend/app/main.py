"""
Main FastAPI application with CORS and comprehensive error handling.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.database import create_tables

# Setup comprehensive logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="WhatsApp Automation MVP - Comprehensive contact management and automation system",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation error",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting WhatsApp Automation MVP...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database URL configured: {bool(settings.DATABASE_URL)}")
    logger.info(f"WhatsApp token configured: {bool(settings.WHATSAPP_TOKEN)}")
    
    try:
        # Create database tables
        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
    
    logger.info("WhatsApp Automation MVP started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down WhatsApp Automation MVP...")
    logger.info("Shutdown completed")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "WhatsApp Automation MVP API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }


@app.get("/test/redis")
async def test_redis_connection():
    """Test Redis connection and task queuing."""
    try:
        from app.core.celery import celery_app
        from app.core.task_queue import TaskQueue
        
        logger.info("Testing Redis connection...")
        
        # Test broker connection
        try:
            stats = celery_app.control.inspect().stats()
            logger.info("✅ Redis broker connection successful")
        except Exception as e:
            logger.error(f"❌ Redis broker connection failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Redis broker connection failed: {str(e)}",
                "broker_url": celery_app.conf.broker_url,
                "result_backend": celery_app.conf.result_backend
            }
        
        # Test task queuing
        try:
            result = celery_app.send_task(
                'app.tasks.automation_tasks.test_connection',
                queue='automation'
            )
            logger.info(f"✅ Test task queued successfully! Task ID: {result.id}")
            
            return {
                "status": "success",
                "message": "Redis connection and task queuing working",
                "task_id": result.id,
                "broker_url": celery_app.conf.broker_url,
                "result_backend": celery_app.conf.result_backend
            }
        except Exception as e:
            logger.error(f"❌ Task queuing failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Task queuing failed: {str(e)}",
                "broker_url": celery_app.conf.broker_url,
                "result_backend": celery_app.conf.result_backend
            }
            
    except Exception as e:
        logger.error(f"❌ Redis test failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Redis test failed: {str(e)}"
        }


@app.get("/test/message-automation/{message_id}")
async def test_message_automation(message_id: int):
    """Test message automation task queuing."""
    try:
        from app.core.task_queue import TaskQueue
        
        logger.info(f"Testing message automation for message {message_id}")
        
        # Queue the task
        success = TaskQueue.queue_message_automation(message_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Message automation queued for message {message_id}",
                "message_id": message_id
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to queue message automation for message {message_id}",
                "message_id": message_id
            }
            
    except Exception as e:
        logger.error(f"❌ Message automation test failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Message automation test failed: {str(e)}",
            "message_id": message_id
        }


# Include API routers
from app.api.messages import router as messages_router
from app.api.webhooks import router as webhooks_router
from app.api.automations import router as automations_router
from app.api.analytics import router as analytics_router
from app.api.contacts import router as contacts_router

app.include_router(messages_router)
app.include_router(webhooks_router)
app.include_router(automations_router)
app.include_router(analytics_router)
app.include_router(contacts_router)

# Note: Background tasks are handled by backend-worker/
# This backend only handles HTTP API requests and queues tasks for workers


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
