#!/bin/bash

set -e

# Wait for database to be ready (if using PostgreSQL)
echo "Waiting for database to be ready..."
python -c "
import os
import time
import django
from django.conf import settings
from django.db import connections
from django.core.management.base import BaseCommand

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medusa.settings')
django.setup()

db_conn = connections['default']
for i in range(30):
    try:
        db_conn.cursor()
        print('Database connection successful')
        break
    except Exception as e:
        print(f'Database connection failed: {e}')
        print('Retrying in 2 seconds...')
        time.sleep(2)
else:
    print('Could not connect to database')
    exit(1)
"

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Create migrations for user specifically
echo "Creating migrations for user"
python manage.py makemigrations user || echo "No changes detected for user app"

# Then create migrations for other apps
echo "Creating migrations for other apps"
python manage.py makemigrations || echo "No changes detected"

# Apply user migrations first
echo "Applying user migrations first"
python manage.py migrate user --database=default || echo "No user migrations to apply"

# Then apply all other migrations
echo "Applying remaining migrations"
python manage.py migrate --database=default

echo "Starting application..."

# Execute the main command
exec "$@"