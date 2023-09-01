import os
from decouple import config
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'friend_trader.settings.{config("ENVIORNMENT")}')

application = get_asgi_application()
