from app.settings import (
    PGDB_NAME,
    PGDB_USER,
    PGDB_PASSWORD,
    PGDB_HOST,
    PGDB_PORT,
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': PGDB_NAME,
        'USER': PGDB_USER,
        'PASSWORD': PGDB_PASSWORD,
        'HOST': PGDB_HOST,
        'PORT': PGDB_PORT,
    }
}
