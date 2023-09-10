from django.urls import path
from rest_framework import routers

from friend_trader_trader.views import FriendTechUserViewSet, FriendTechUserListView

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'friend-tech-user', FriendTechUserViewSet)


urlpatterns = [
    path("friend-tech-user-list/", FriendTechUserListView.as_view())
]

urlpatterns += router.urls