#!/bin/sh

set -e

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Creating database migrations
echo "Collecting database migrations"
python manage.py makemigrations --merge --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --database=default

# Create superuser if not exists
echo "Creating superuser"
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@medusa.com', 'test1234')
"

# Start ASGI app with Uvicorn
echo "Starting ASGI app with Uvicorn"
exec uvicorn medusa.asgi:application --host 0.0.0.0 --port 5000 --reload
