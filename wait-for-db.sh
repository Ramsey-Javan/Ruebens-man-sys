#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."

# Wait until the app database is available
until pg_isready -h db -U user -d app > /dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL is ready. Starting Flask..."
echo "Loaded DATABASE_URL: $DATABASE_URL"

# Run Flask
exec gunicorn -w 4 -b 0.0.0.0:5000 website.wsgi:app

