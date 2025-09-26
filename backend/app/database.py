"""
Database configuration and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create database engine
logger.info(f"Creating database engine with URL: {os.getenv('DATABASE_URL', 'Not set')[:20]}...")
engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Database session factory created")

# Create declarative base
Base = declarative_base()
logger.info("Database base class created")

# IMPORTANT: Import all model modules so SQLAlchemy registers their tables
# before calling Base.metadata.create_all(). Without these imports, foreign
# keys like messages.created_by -> users.id may fail if the target table
# isn't loaded into the metadata yet.
from app.models import user  # noqa: F401
from app.models import contact  # noqa: F401
from app.models import message  # noqa: F401
from app.models import automation  # noqa: F401
from app.models import automation_log  # noqa: F401


def get_db():
    """
    Dependency to get database session.
    """
    logger.debug("Creating database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()


def create_tables():
    """
    Create all tables in the database.
    """
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def drop_tables():
    """
    Drop all tables in the database.
    """
    logger.warning("Dropping all database tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise
