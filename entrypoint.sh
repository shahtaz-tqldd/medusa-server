#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."

function postgres_ready() {
python << END
import sys
import psycopg2
import time

db_config = {
    "dbname": "${PGDB_NAME}",
    "user": "${PGDB_USER}",
    "password": "${PGDB_PASSWORD}",
    "host": "${PGDB_HOST}",
    "port": int("${PGDB_PORT}"),
}

max_attempts = 10
for attempt in range(max_attempts):
    try:
        conn = psycopg2.connect(**db_config)
        conn.close()
        sys.exit(0)
    except psycopg2.OperationalError:
        time.sleep(2)
sys.exit(1)
END
}

# Loop until Postgres is ready
until postgres_ready; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 2
done

>&2 echo "Postgres is up - executing commands"

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --noinput

# Create superuser if not exists
echo "Creating superuser if not exists"
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
END

# Start the application
exec "$@"
