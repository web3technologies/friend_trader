from django.db.utils import IntegrityError

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT


from friend_trader_core.mixins import ThrottleMixin
from friend_trader_trader.models import FriendTechUserWatchList
from friend_trader_trader.serializers import FriendTechUserWatchListSeriazlier, FriendTechUserWatchListSeriazlierCreate



class FriendTechUserWatchListViewset(ModelViewSet, ThrottleMixin):
    
    queryset = FriendTechUserWatchList.objects.all()
    serializer_class = FriendTechUserWatchListSeriazlier
    permission_classes = [ IsAuthenticated ]
    http_method_names = ["get", "post", "head", "patch", "delete"]
    
    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FriendTechUserWatchListSeriazlier
        if self.action == "create":
            return FriendTechUserWatchListSeriazlierCreate
        return super().get_serializer_class()
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(data={"Watch Relation Already Exists"}, status=HTTP_400_BAD_REQUEST)
    
    @action(
        detail=False,
        methods=["delete"],
        url_path="remove-watch",
        name="remove_watch",
    )
    def remove_watch(self, request, *args, **kwargs):
        self.queryset.get(user=request.user, friend_tech_user_id=request.data.get("friend_tech_user_id")).delete()
        return Response(data={"detail": "removed"}, status=HTTP_204_NO_CONTENT)