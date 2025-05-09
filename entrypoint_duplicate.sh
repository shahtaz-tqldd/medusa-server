#!/bin/sh
# This script automatically handles migration order issues

# Function to check if migration table exists
check_migration_table() {
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medusa.settings')
django.setup()
from django.db import connections
with connections['default'].cursor() as cursor:
    cursor.execute(\"\"\"
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'django_migrations'
        );
    \"\"\")
    exists = cursor.fetchone()[0]
    exit(0 if exists else 1)
"
    return $?
}

# Function to check if admin migrations are applied before user migrations
check_migration_order() {
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medusa.settings')
django.setup()
from django.db import connections
with connections['default'].cursor() as cursor:
    cursor.execute(\"\"\"
        SELECT EXISTS (
            SELECT 1 FROM django_migrations
            WHERE app = 'admin' AND name = '0001_initial'
        );
    \"\"\")
    admin_exists = cursor.fetchone()[0]
    
    cursor.execute(\"\"\"
        SELECT EXISTS (
            SELECT 1 FROM django_migrations
            WHERE app = 'user' AND name = '0001_initial'
        );
    \"\"\")
    user_exists = cursor.fetchone()[0]
    
    # Exit 0 if order is correct (user exists or admin doesn't exist)
    # Exit 1 if order is wrong (admin exists but user doesn't)
    exit(0 if (user_exists or not admin_exists) else 1)
"
    return $?
}

# Function to temporarily modify settings.py to disable admin
modify_settings() {
    # Create backup
    cp medusa/settings.py medusa/settings.py.bak
    
    # Comment out admin from INSTALLED_APPS
    sed -i "s/'django.contrib.admin',/# 'django.contrib.admin',/" medusa/settings.py
    
    echo "Temporarily disabled admin in settings.py"
}

# Function to restore settings.py
restore_settings() {
    if [ -f "medusa/settings.py.bak" ]; then
        mv medusa/settings.py.bak medusa/settings.py
        echo "Restored original settings.py"
    fi
}

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Check if we need to fix migration order
if check_migration_table; then
    echo "Migration table exists, checking order..."
    if ! check_migration_order; then
        echo "FIXING: Admin migrations found before user migrations"
        
        # Backup and modify settings
        modify_settings
        
        # Create user migrations
        echo "Creating user migrations"
        python manage.py makemigrations user
        
        # Apply user migrations first
        echo "Applying user migrations"
        python manage.py migrate user --database=default
        
        # Restore settings
        restore_settings
        
        echo "Migration order fixed, continuing with normal process"
    else
        echo "Migration order is correct, proceeding normally"
    fi
else
    echo "Fresh database, proceeding with normal migration process"
    # For fresh installs, ensure user migrations are created first
    python manage.py makemigrations user
fi

# Create remaining migrations
echo "Creating migrations for other apps"
python manage.py makemigrations --merge --noinput

# Apply remaining migrations
echo "Applying remaining migrations"
python manage.py migrate --database=default

echo "Starting development server"
python manage.py runserver 0.0.0.0:5000