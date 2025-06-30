#!/bin/sh

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Creating database migrations
echo "collecting database migrations"
python manage.py makemigrations --merge --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --database=default

# Create superuser if it doesn't exist
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
    
echo "Starting development server"
python manage.py runserver 0.0.0.0:5000

