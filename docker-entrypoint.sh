#!/bin/bash

echo 'Running migrations...'
python3 manage.py migrate

echo 'Collecting static files...'
python3 manage.py collectstatic --no-input

echo "Starting server..."
uwsgi --ini uwsgi.ini
