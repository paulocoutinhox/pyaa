#!/bin/bash
set -e

echo "Running migrations..."
python3 manage.py migrate

echo "Building frontend assets..."
make frontend-prod

echo "Compiling SCSS files..."
python3 manage.py compilescss

echo "Collecting static files..."
python3 manage.py collectstatic --no-input

WORKERS=$((2 * $(nproc) + 1))
echo "Starting async server with $WORKERS workers..."

exec gunicorn pyaa.asgi:application \
  --bind 0.0.0.0:8000 \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers "$WORKERS" \
  --worker-connections 1000 \
  --timeout 60 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --preload \
  --access-logfile - \
  --error-logfile - \
  --log-level info
