#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python3 manage.py migrate

# create super user
echo "Create super user"
python3 manage.py createsuperuser --noinput

# Start server
echo "Starting server"
uwsgi --ini uwsgi.ini
