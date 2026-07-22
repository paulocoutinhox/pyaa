#!/bin/bash
set -e

echo "Running migrations..."
python3 manage.py migrate

echo "Building frontend assets..."
make frontend-prod

echo "Collecting static files..."
python3 manage.py collectstatic --no-input

echo "Exporting environment variables..."
printenv > /etc/environment

# workers count used by the async web program in supervisord
WORKERS=$((2 * $(nproc) + 1))
export WORKERS

echo "Starting supervisor..."
exec supervisord -n -c /app/supervisord.all.async.web.conf
