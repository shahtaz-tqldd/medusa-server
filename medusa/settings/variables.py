import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv()

SECRET_KEY = os.getenv('APP_SECRET_KEY')
DEBUG = os.getenv('APP_ENV') == 'dev'

ALLOWED_HOSTS = [host.strip() for host in (os.getenv('ALLOWED_HOSTS') or '').split(',') if host.strip()]

ROOT_URLCONF = 'medusa.urls'

# JWT

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=4),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# database
PGDB_NAME = os.getenv('PGDB_NAME', 'medusa_db')
PGDB_USER = os.getenv('PGDB_USER', 'medusa_owner')
PGDB_PASSWORD = os.getenv('PGDB_PASSWORD', 'cleanCodeMyth')
PGDB_HOST = os.getenv('PGDB_HOST', 'db')
PGDB_PORT = os.getenv('PGDB_PORT', '5431')

# email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

#language
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# secret 
USER_CREATE_SECRET = os.getenv('USER_CREATE_SECRET')

#static url
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# media url
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR, 'media'