#!/bin/bash

# Database Setup Script Wrapper for FedFina
# This script sets up the PostgreSQL database, user, and tables

set -e  # Exit on any error

echo "=========================================="
echo "FedFina Database Setup Script"
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "scripts/setup_database.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "❌ Error: PostgreSQL is not running on localhost:5432"
    echo "Please start PostgreSQL first"
    exit 1
fi

echo "✅ PostgreSQL is running"
echo "🚀 Starting database setup..."

# Run the Python setup script
python3 scripts/setup_database.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Database setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Database Details:"
    echo "- Database: fedfina_enhanced_reporting"
    echo "- User: fedfina_app_user"
    echo "- Connection: postgresql://fedfina_app_user:fedfina_app_password_2025@localhost:5432/fedfina_enhanced_reporting"
    echo ""
    echo "You can now start the FedFina application."
else
    echo ""
    echo "❌ Database setup failed!"
    exit 1
fi 