#!/bin/bash
# entrypoint.sh

echo "[INIT] Running database migrations..."
flask db upgrade

echo "[INIT] Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:5000 "website.wsgi:app"
