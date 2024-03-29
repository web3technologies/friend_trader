from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('friend-trader/', include("friend_trader_trader.urls")),
    path("auth/", include("friend_trader_auth.urls"))
]