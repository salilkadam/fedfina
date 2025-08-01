# Database Setup Scripts for FedFina

This directory contains scripts to set up the PostgreSQL database for the FedFina Enhanced Reporting system.

## Files

- `setup_database.py` - Main Python script that creates database, user, and tables
- `setup_db.sh` - Shell script wrapper for easy execution
- `README_DATABASE.md` - This documentation file

## Prerequisites

1. **PostgreSQL** must be installed and running on localhost:5432
2. **Python 3** with the following packages:
   - `sqlalchemy`
   - `psycopg2-binary`
   - `python-dotenv`

## Quick Setup

### Option 1: Using the shell script (Recommended)

```bash
# From the project root directory
./scripts/setup_db.sh
```

### Option 2: Using the Python script directly

```bash
# From the project root directory
python3 scripts/setup_database.py
```

## What the Scripts Do

### 1. Database Creation
- Creates database `fedfina_enhanced_reporting` if it doesn't exist
- Sets proper encoding and ownership

### 2. User Management
- Creates user `fedfina_app_user` with password `fedfina_app_password_2025`
- Grants necessary privileges for database operations

### 3. Table Creation
- Creates all tables defined in SQLAlchemy models
- Currently creates `client_interviews` table with the following columns:
  - `id` (Primary Key)
  - `conversation_id` (Unique)
  - `officer_name`
  - `officer_email`
  - `client_account_id`
  - `minio_audio_url`
  - `minio_transcript_url`
  - `minio_report_url`
  - `interview_date`
  - `status`
  - `created_at`
  - `updated_at`

### 4. Connection Testing
- Verifies that the application can connect to the database
- Tests basic database operations

## Database Configuration

The scripts use the following configuration:

```python
DB_NAME = "fedfina_enhanced_reporting"
DB_USER = "fedfina_app_user"
DB_PASSWORD = "fedfina_app_password_2025"
DB_HOST = "localhost"
DB_PORT = "5432"
```

## Connection String

After setup, the application uses this connection string:
```
postgresql://fedfina_app_user:fedfina_app_password_2025@localhost:5432/fedfina_enhanced_reporting
```

## Environment Variables

The backend `.env` file should contain:
```env
DATABASE_URL=postgresql://fedfina_app_user:fedfina_app_password_2025@localhost:5432/fedfina_enhanced_reporting
```

## Troubleshooting

### PostgreSQL Not Running
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# If not running, start it (Ubuntu/Debian)
sudo systemctl start postgresql
```

### Permission Issues
```bash
# Make sure scripts are executable
chmod +x scripts/setup_db.sh
chmod +x scripts/setup_database.py
```

### Python Dependencies
```bash
# Install required packages
pip3 install sqlalchemy psycopg2-binary python-dotenv
```

### Database Already Exists
The scripts are idempotent - they can be run multiple times safely. If the database or user already exists, the scripts will skip creation and continue with the setup.

## Manual Database Operations

### Connect to Database
```bash
# As postgres user
psql -U postgres -d fedfina_enhanced_reporting

# As application user
PGPASSWORD=fedfina_app_password_2025 psql -U fedfina_app_user -d fedfina_enhanced_reporting
```

### List Tables
```sql
\dt
```

### Check Table Structure
```sql
\d client_interviews
```

### Drop Database (if needed)
```sql
-- Connect as postgres user
DROP DATABASE fedfina_enhanced_reporting;
```

## Integration with Application

The database setup is automatically handled by the `DatabaseService` class in `backend/services/database_service.py`. The service:

1. Connects to the database using the `DATABASE_URL` environment variable
2. Creates tables automatically if they don't exist
3. Provides CRUD operations for client interviews

## Security Notes

- The database user has minimal required privileges
- Passwords are hardcoded in the script for development - should be externalized for production
- Consider using environment variables for sensitive configuration in production

## Production Considerations

For production deployment:

1. Use environment variables for database credentials
2. Implement proper backup strategies
3. Consider using connection pooling
4. Set up monitoring and logging
5. Use SSL connections if required
6. Implement proper access controls 