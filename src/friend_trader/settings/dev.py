from .settings import *


ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'friend_trader',
        'USER': 'friend_trader',
        'PASSWORD': "Testing321.",
        'HOST': "localhost",
        'PORT': '5432',
    }
}