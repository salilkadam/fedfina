#!/usr/bin/env python3
"""
Database Setup Script for FedFina Enhanced Reporting
Creates database, user, and tables if they don't exist
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add backend to path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.database_service import Base, ClientInterview

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_NAME = "fedfina_enhanced_reporting"
DB_USER = "fedfina_app_user"
DB_PASSWORD = "fedfina_app_password_2025"
DB_HOST = "localhost"
DB_PORT = "5432"

# Connection strings
POSTGRES_CONNECTION = f"postgresql://postgres@{DB_HOST}:{DB_PORT}/postgres"
APP_DB_CONNECTION = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Connect to PostgreSQL as postgres user
        conn = psycopg2.connect(POSTGRES_CONNECTION)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER postgres")
            logger.info(f"Database '{DB_NAME}' created successfully")
        else:
            logger.info(f"Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False

def create_user_if_not_exists():
    """Create database user if it doesn't exist"""
    try:
        # Connect to PostgreSQL as postgres user
        conn = psycopg2.connect(POSTGRES_CONNECTION)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (DB_USER,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating user '{DB_USER}'...")
            cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}'")
            logger.info(f"User '{DB_USER}' created successfully")
        else:
            logger.info(f"User '{DB_USER}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return False

def grant_privileges():
    """Grant necessary privileges to the user"""
    try:
        # Connect to PostgreSQL as postgres user
        conn = psycopg2.connect(POSTGRES_CONNECTION)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("Granting privileges to user...")
        
        # Grant connect privilege on database
        cursor.execute(f"GRANT CONNECT ON DATABASE {DB_NAME} TO {DB_USER}")
        
        # Connect to the application database to grant schema privileges
        cursor.close()
        conn.close()
        
        # Connect to application database as postgres user
        app_conn = psycopg2.connect(f"postgresql://postgres@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        app_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        app_cursor = app_conn.cursor()
        
        # Grant schema privileges
        app_cursor.execute(f"GRANT USAGE ON SCHEMA public TO {DB_USER}")
        app_cursor.execute(f"GRANT CREATE ON SCHEMA public TO {DB_USER}")
        app_cursor.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {DB_USER}")
        app_cursor.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {DB_USER}")
        app_cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {DB_USER}")
        app_cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {DB_USER}")
        
        app_cursor.close()
        app_conn.close()
        
        logger.info("Privileges granted successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error granting privileges: {str(e)}")
        return False

def create_tables():
    """Create tables using SQLAlchemy models"""
    try:
        logger.info("Creating tables...")
        
        # Create engine for application database
        engine = create_engine(APP_DB_CONNECTION, echo=False)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Tables created: {tables}")
        
        # Check specific table structure
        if 'client_interviews' in tables:
            columns = inspector.get_columns('client_interviews')
            logger.info(f"client_interviews table columns: {[col['name'] for col in columns]}")
        
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

def test_connection():
    """Test database connection with application user"""
    try:
        logger.info("Testing database connection...")
        
        engine = create_engine(APP_DB_CONNECTION, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Database connection successful: {version}")
        
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    logger.info("Starting database setup...")
    
    # Step 1: Create database
    if not create_database_if_not_exists():
        logger.error("Failed to create database")
        sys.exit(1)
    
    # Step 2: Create user
    if not create_user_if_not_exists():
        logger.error("Failed to create user")
        sys.exit(1)
    
    # Step 3: Grant privileges
    if not grant_privileges():
        logger.error("Failed to grant privileges")
        sys.exit(1)
    
    # Step 4: Create tables
    if not create_tables():
        logger.error("Failed to create tables")
        sys.exit(1)
    
    # Step 5: Test connection
    if not test_connection():
        logger.error("Failed to test connection")
        sys.exit(1)
    
    logger.info("Database setup completed successfully!")
    logger.info(f"Database: {DB_NAME}")
    logger.info(f"User: {DB_USER}")
    logger.info(f"Connection string: {APP_DB_CONNECTION}")

if __name__ == "__main__":
    main() 