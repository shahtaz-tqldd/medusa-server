import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv()

SECRET_KEY = os.getenv('APP_SECRET_KEY')
DEBUG = os.getenv('APP_ENV') == 'dev'

ALLOWED_HOSTS = [host.strip() for host in (os.getenv('ALLOWED_HOSTS') or '').split(',') if host.strip()]

ROOT_URLCONF = 'medusa.urls'

# database
PGDB_NAME = os.getenv('PGDB_NAME', 'medusa_db')
PGDB_USER = os.getenv('PGDB_USER', 'medusa_owner')
PGDB_PASSWORD = os.getenv('PGDB_PASSWORD', 'cleanCodeMyth')
PGDB_HOST = os.getenv('PGDB_HOST', 'db')
PGDB_PORT = os.getenv('PGDB_PORT', '5431')

#language
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

#static url
STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')