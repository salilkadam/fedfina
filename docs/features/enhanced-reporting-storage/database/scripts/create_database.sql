-- Database Setup Script for FedFina Enhanced Reporting
-- Description: Creates the database and user for the enhanced reporting system
-- Date: July 31, 2025
-- Author: AI Assistant

-- Connect to PostgreSQL as superuser (postgres)
-- This script should be run as a PostgreSQL superuser

-- Create the database if it doesn't exist
CREATE DATABASE fedfina_enhanced_reporting
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Create a dedicated user for the application
CREATE USER fedfina_app_user WITH PASSWORD 'fedfina_app_password_2025';

-- Grant necessary privileges to the user
GRANT CONNECT ON DATABASE fedfina_enhanced_reporting TO fedfina_app_user;
GRANT USAGE ON SCHEMA public TO fedfina_app_user;
GRANT CREATE ON SCHEMA public TO fedfina_app_user;

-- Connect to the new database
\c fedfina_enhanced_reporting;

-- Grant additional privileges in the new database
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fedfina_app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fedfina_app_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO fedfina_app_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fedfina_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fedfina_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO fedfina_app_user;

-- Create extensions that might be needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Verify the setup
SELECT 
    datname as database_name,
    datdba as owner,
    encoding,
    datcollate,
    datctype
FROM pg_database 
WHERE datname = 'fedfina_enhanced_reporting';

-- List the created user
SELECT 
    usename as username,
    usecreatedb as can_create_db,
    usesuper as is_superuser
FROM pg_user 
WHERE usename = 'fedfina_app_user';

-- Output connection information
\echo 'Database setup completed successfully!'
\echo 'Database Name: fedfina_enhanced_reporting'
\echo 'Username: fedfina_app_user'
\echo 'Password: fedfina_app_password_2025'
\echo ''
\echo 'Connection string:'
\echo 'postgresql://fedfina_app_user:fedfina_app_password_2025@localhost:5432/fedfina_enhanced_reporting'
\echo ''
\echo 'Next steps:'
\echo '1. Update your .env file with the connection string above'
\echo '2. Run the migration scripts to create tables'
\echo '3. Test the database connection' 