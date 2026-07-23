#!/bin/bash
set -e

echo 'Running migrations...'
python3 manage.py migrate

echo 'Building frontend assets...'
make frontend-prod

echo 'Collecting static files...'
python3 manage.py collectstatic --no-input

echo 'Exporting environment variables...'
printenv > /etc/environment

echo 'Starting supervisor...'
exec supervisord -n -c /app/supervisord.all.web.conf
