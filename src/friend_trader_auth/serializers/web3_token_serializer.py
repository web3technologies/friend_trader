from ipaddress import ip_address
from django.contrib.auth import get_user_model
from web3 import Web3
from hexbytes import HexBytes
from eth_account.messages import encode_defunct
import uuid
import logging
from friend_trader_auth.utils.message import gen_message
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from friend_trader_auth.models import Connection
from friend_trader_auth.serializers.user_serializer import FriendTraderUserSerializer

logger = logging.getLogger(__file__)


class FriendTraderTokenObtainSerializer(TokenObtainPairSerializer):
    """
        Custom authentication Backend for login with private key signature
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']

    signature = serializers.CharField()
    message = serializers.CharField()
    ip_address = serializers.CharField()

    def validate(self, attrs):

        usermodel = get_user_model()
        self._check_model_attributes(usermodel)

        signature = attrs.get('signature')
        public_address = attrs.get("public_address")

        if public_address and signature:
            try:
                user = usermodel.objects.get(public_address=public_address)
                message=encode_defunct(text=str(gen_message(user.nonce)))
                w3 = Web3(Web3.HTTPProvider(""))
                verified_public_address = w3.eth.account.recover_message(
                    message,
                    signature=HexBytes(signature)
                )
                sent_address_from_request = attrs.get('public_address')
                if verified_public_address == sent_address_from_request:
                    user.nonce = uuid.uuid4()
                    user.save()
                    conn = Connection.objects.create(
                        user=user,
                        ip_address=ip_address
                    )
                    logger.info(f"CONNECTION created from ip_address {conn.ip_address}")
                    refresh = RefreshToken.for_user(user)
                    data = {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "user": FriendTraderUserSerializer(user).data
                    }
                    logger.info(f"SUCCCESS user logged in {verified_public_address}")
                    return data
                else:
                    logger.warn(f"Sig incorrect for address {sent_address_from_request}")
                    return None
                
            except usermodel.DoesNotExist:
                logger.warn("user does not exist")
                return None
            except Exception as e:
                logger.warn(str(e.args))
                return None
        else:
            logger.warn("No pub or sig")
            return None

    def get_user(self, user_id):
        usermodel = get_user_model()
        try:
            return usermodel.objects.get(pk=user_id)
        except usermodel.DoesNotExist:
            return None

    def _check_model_attributes(self, usermodel):

        if not hasattr(usermodel, 'nonce'):
            raise AttributeError("nonce is a required field in the user model")