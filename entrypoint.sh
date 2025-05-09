#!/bin/sh

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# First create migrations for user app specifically
echo "Creating migrations for user app"
python manage.py makemigrations user

# Then create migrations for other apps
echo "Creating migrations for other apps"
python manage.py makemigrations --merge --noinput

# Apply user migrations first
echo "Applying user migrations first"
python manage.py migrate user --database=default

# Then apply all other migrations
echo "Applying remaining migrations"
python manage.py migrate --database=default

echo "Starting development server"
python manage.py runserver 0.0.0.0:5000