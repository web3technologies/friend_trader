from pathlib import Path
from datetime import timedelta
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SECRET_KEY = config("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_celery_beat",
    "django_celery_results",
    "django_extensions",
    "friend_trader_auth",
    "friend_trader_dispatcher",
    "friend_trader_trader",
    "web_socket_manager"
]
AUTH_USER_MODEL = 'friend_trader_auth.User'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'friend_trader.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'friend_trader.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'friend_trader',
        'USER': 'friend_trader',
        'PASSWORD': 'Testing321.',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CELERY_BROKER_URL = 'amqp://'

CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXPIRES = timedelta(days=30)
CELERY_TASK_TRACK_STARTED = True
CELERY_ENABLE_REMOTE_CONTROL = False
CELERY_SEND_EVENTS = False
CELERY_COUNTDOWN = 5


BLAST_WSS_API=config('BLAST_WSS_API')
DISCORD_WEBHOOK=config("DISCORD_WEBHOOK")
DISCORD_WEBHOOK_NEW_USER_GREATER_THAN_100K=config("DISCORD_WEBHOOK_NEW_USER_GREATER_THAN_100K")
TWITTER_CONSUMER_KEY=config('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET=config('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN=config('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET=config('TWITTER_ACCESS_TOKEN_SECRET')


#block at which the contract was deployed
INITIAL_BLOCK = 2430440
