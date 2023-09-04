from rest_framework import routers

from friend_trader_trader.views import FriendTechUserViewSet

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'friend-tech-users', FriendTechUserViewSet)


urlpatterns = [
    
]

urlpatterns += router.urls