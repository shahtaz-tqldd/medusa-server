DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'django_filters',
    'django_celery_beat',
    'django_celery_results',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
]

DEVELOPED_APPS = [
    'base',
    'user',
    'projects',
    'services',
    'blogs',
    'chat',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + DEVELOPED_APPS