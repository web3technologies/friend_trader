from django.urls import path
from friend_trader_auth.views import FriendTraderAuthView, FriendTraderNonceView, FriendTraderUserView


urlpatterns = [
    path(r'authenticate', FriendTraderAuthView.as_view(), name="web3-authenticate"),
    path(r'nonce', FriendTraderNonceView.as_view(), name="web3-nonce"),
    path("user/", FriendTraderUserView.as_view(), name="user")
]