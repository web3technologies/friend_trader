from .settings import *


ALLOWED_HOSTS = ["friendtrader.tech", "backend.friendtrader.tech"]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://friendtrader.tech"
]

MEDIA_ROOT = "/applications/friend_trader/"
STATIC_ROOT = f"/applications/friend_trader/static/"

TEMPLATES[0]['DIRS'] = [STATIC_ROOT]

DEBUG = False


CELERY_BROKER_URL = "sqs://"
CELERY_TASK_DEFAULT_QUEUE = 'friend_trader'


CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'us-east-2',
    'is_secure': True,
    'predefined_queues': {
        'friend_trader': {
            'url': 'https://sqs.us-east-2.amazonaws.com/490305332793/friend_trader',
        },
    },
    'visibility_timeout': 3600,
    'polling_interval': 5.0,
}