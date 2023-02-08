#!/bin/bash

# Collect static files
echo "Collect static files"
python3 manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python3 manage.py migrate

# create super user
echo "Create super user"
python3 manage.py createsuperuser --noinput

# Start server
echo "Starting server"
python3 manage.py runserver 0.0.0.0:8000
