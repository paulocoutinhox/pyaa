#!/bin/bash
set -e

echo 'Running migrations...'
python3 manage.py migrate

echo 'Building frontend assets...'
make frontend-prod

echo 'Compiling SCSS files...'
python3 manage.py compilescss

echo 'Collecting static files...'
python3 manage.py collectstatic --no-input

echo "Starting server..."
uwsgi --ini uwsgi.ini
