#!/bin/sh

# Collect static files
echo "Collecting static files"
python manage.py collectstatic

# First create migrations for user specifically
echo "Creating migrations for user"
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
