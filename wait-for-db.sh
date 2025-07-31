#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."

# Wait until the app database is available
until pg_isready -h db -U user -d app > /dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL is ready. Starting Flask..."
echo "Loaded DATABASE_URL: $DATABASE_URL"

# Run Flask
exec gunicorn website.wsgi:app --bind 0.0.0.0:5000 --workers 3 --timeout 120 --log-level info
# Note: Ensure that the DATABASE_URL environment variable is set correctly in your environment.

