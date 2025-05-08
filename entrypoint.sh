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


echo "Starting ASGI app with Uvicorn"
uvicorn medusa.asgi:application --host 0.0.0.0 --port 5000 --reload
