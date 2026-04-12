#!/bin/bash
# Quick script to apply Migration 007

set -e

echo "========================================="
echo "Applying Migration 007"
echo "Fix review_decisions.decision field length"
echo "========================================="

# Load environment variables if .env exists
if [ -f "../../apps/api/.env" ]; then
    export $(cat ../../apps/api/.env | grep -v '^#' | xargs)
fi

# Set default values
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-ai_comic_drama}
DB_USER=${DB_USER:-postgres}

echo ""
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"
echo ""

# Apply migration
echo "Applying migration..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f 007_fix_review_decision_length.sql

echo ""
echo "✅ Migration 007 applied successfully!"
echo ""

# Run test
echo "Running verification tests..."
python test_007_migration.py

echo ""
echo "========================================="
echo "Migration 007 complete!"
echo "========================================="
