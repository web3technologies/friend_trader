from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import logging
from friend_trader_auth.utils.message import gen_message
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from friend_trader_auth.serializers.web3_token_serializer import FriendTraderTokenObtainSerializer
from friend_trader_auth.serializers.user_serializer import FriendTraderUserSerializer

logger = logging.getLogger(__file__)


class FriendTraderAuthView(TokenObtainPairView):
    serializer_class = FriendTraderTokenObtainSerializer

class FriendTraderNonceView(APIView):

    def post(self, request):
        public_address = request.data.get('public_address')

        if not public_address:
            return Response(data={"detail": "Must Provide Address"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(public_address=public_address)
        if created:
            user.set_unusable_password() 
        logger.info(f"RETRIEVING NONCE FOR ADDRESS {public_address}")

        nonce = user.nonce

        msg = gen_message(nonce)

        return Response(data={"message": msg}, status=status.HTTP_200_OK)
    
    
    
class FriendTraderUserView(APIView):
    
    serializer_class = FriendTraderUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        data = self.serializer_class(request.user).data
        return Response(data=data, status=status.HTTP_200_OK)