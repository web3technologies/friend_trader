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
    'corsheaders',
    "rest_framework",
    "rest_framework_simplejwt",
    "friend_trader_auth",
    "friend_trader_async",
    "friend_trader_trader",
    "web_socket_manager"
]
AUTH_USER_MODEL = 'friend_trader_auth.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

REST_FRAMEWORK = {
    'DEFAULT_SERIALIZER_CLASSES': {
        'depth': 3  # Ensure depth is sufficient to serialize A -> B -> C
    },
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'ANONYMOUS_THROTTLE_RATE': '100/hour',   # example rate
    'ANONYMOUS_THROTTLE_CLASS': 'rest_framework.throttling.AnonRateThrottle',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',)
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console":{
            "class": "logging.StreamHandler"
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            "level": "INFO"
        },
        'friend_trader_trader': {
            'handlers': ['console'],
            'propagate': True,
        },
        'friend_trader_async': {
            'handlers': ['console'],
            'propagate': True,
        }
    }
}



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

TWITTER_CONSUMER_KEY_1=config('TWITTER_CONSUMER_KEY_1')
TWITTER_CONSUMER_SECRET_1=config('TWITTER_CONSUMER_SECRET_1')
TWITTER_ACCESS_TOKEN_1=config('TWITTER_ACCESS_TOKEN_1')
TWITTER_ACCESS_TOKEN_SECRET_1=config('TWITTER_ACCESS_TOKEN_SECRET_1')

TWITTER_CONSUMER_KEY_2=config('TWITTER_CONSUMER_KEY_2')
TWITTER_CONSUMER_SECRET_2=config('TWITTER_CONSUMER_SECRET_2')
TWITTER_ACCESS_TOKEN_2=config('TWITTER_ACCESS_TOKEN_2')
TWITTER_ACCESS_TOKEN_SECRET_2=config('TWITTER_ACCESS_TOKEN_SECRET_2')



#block at which the contract was deployed
#INITIAL_BLOCK = 2430440
#INITIAL_BLOCK = 3_263_684
INITIAL_BLOCK = 2_763_440