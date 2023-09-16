from .settings import *



ALLOWED_HOSTS = ["https://backend.friendtrader.tech"]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://friendtrader.tech"
]

MEDIA_ROOT = "/applications/friend_trader/"
STATIC_ROOT = f"/applications/friend_trader/static/"

TEMPLATES[0]['DIRS'] = [STATIC_ROOT]

DEBUG = True