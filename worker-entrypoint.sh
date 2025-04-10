#!/bin/bash

echo "Starting django-q worker..."
exec python3 manage.py qcluster
