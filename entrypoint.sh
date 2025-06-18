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

# starting development server
echo "Starting development server"
python manage.py runserver 0.0.0.0:5000