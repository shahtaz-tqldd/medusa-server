#!/bin/sh

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z medusa_db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Creating database migrations
echo "Creating database migrations"
python manage.py makemigrations --merge --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --database=default

# Create superuser if it doesn't exist (only in development)
if [ "$APP_ENV" = "dev" ]; then
    echo "Checking for superuser"
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username="$DJANGO_SUPERUSER_USERNAME",
        email="$DJANGO_SUPERUSER_EMAIL",
        password="$DJANGO_SUPERUSER_PASSWORD"
    )
    print("Superuser created successfully")
else:
    print("Superuser already exists")
EOF
fi

# Check if running in production
if [ "$APP_ENV" = "prod" ]; then
    echo "Starting production server with Gunicorn"
    # Install gunicorn if not in requirements
    pip install gunicorn
    # Start Gunicorn with optimal settings
    exec gunicorn \
        --bind 0.0.0.0:5000 \
        --workers 4 \
        --worker-class sync \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 2 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --capture-output \
        myproject.wsgi:application
else
    echo "Starting development server"
    python manage.py runserver 0.0.0.0:5000
fi