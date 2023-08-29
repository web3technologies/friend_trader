

from django.conf import settings
import datetime
import json
import pytz
import random
import requests
import tweepy
from tweepy.errors import NotFound, TweepyException
from web3 import Web3

from friend_trader_trader.models import FriendTechUser


class TwitterForbiddenException(Exception):
    ...

class BlockActions:
    blast_url = f"https://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    ankr_url = "https://rpc.ankr.com/base"
    CONTRACT_ADDRESS = "0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4"
    KOSSETTO_URL = "https://prod-api.kosetto.com/users"
    
    def __init__(self) -> None:
        twitter_auth = tweepy.OAuth1UserHandler(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.web3_providers = [
            Web3(Web3.HTTPProvider(self.ankr_url)),
            Web3(Web3.HTTPProvider(self.blast_url))
        ]
        self.tweepy_client = tweepy.API(twitter_auth)
        self.web3 = random.choice(self.web3_providers)
        with open(settings.BASE_DIR / "src" / "web_socket_manager" / "abi.json", "r") as abis:
            contract_abis = json.loads(abis.read())
        self.contract = self.web3.eth.contract(address=self.CONTRACT_ADDRESS, abi=contract_abis)
        self.friend_tech_users_to_create = {}
        
    def __send_discord_messages(self, notification, webhook_url):
        embed = {
            "title": notification['twitter_name'],
            "url": f"https://twitter.com/{notification['twitter_name']}",
            "description": notification["msg"],
            "color": 7506394,
            "thumbnail": {
                "url": notification["image_url"]
            }
        }
        payload = {
            "embeds": [embed]
        }
        response = requests.post(webhook_url, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print(f"Payload delivered successfully, code {response.status_code}.")
            
            
    def __convert_to_central_time(self, eth_timestamp):
        utc_time = datetime.datetime.utcfromtimestamp(eth_timestamp)
        utc_time = pytz.utc.localize(utc_time)
        central_time = utc_time.astimezone(pytz.timezone('US/Central'))
        return central_time
    
    def __manage_friend_tech_user(self, shares_subject):
        try:
            friend_tech_user = FriendTechUser.objects.get(address=shares_subject)
            twitter_username = friend_tech_user.twitter_username
            profile_pic_url = friend_tech_user.twitter_profile_pic
        except FriendTechUser.DoesNotExist:
            res = requests.get(f"{self.KOSSETTO_URL}/{shares_subject}", timeout=3)
            res.raise_for_status()
            kossetto_data = res.json()
            twitter_username = kossetto_data.get("twitterUsername")
            profile_pic_url = kossetto_data.get("twitterPfpUrl")
            if twitter_username not in self.friend_tech_users_to_create:
                self.friend_tech_users_to_create[twitter_username] = (
                   FriendTechUser(
                        address=shares_subject,
                        twitter_username=twitter_username,
                        twitter_profile_pic=kossetto_data.get("twitterPfpUrl")
                    ) 
                )
                    
        return twitter_username, profile_pic_url
        
    
    def __perform_block_actions(self, block_hash):
        twitter_userdata, notification_data = [], []
        block = self.web3.eth.get_block(block_hash, full_transactions=True)
        print(f"Block # {block.number}")
        print(self.web3.provider.endpoint_uri)
        for tx in block.transactions:
            if tx["to"] == self.contract.address:
                function, function_input = self.contract.decode_function_input(tx.input)
                if function.function_identifier == "buyShares":
                    try:
                        shares_subject = function_input.get('sharesSubject')
                        twitter_username, profile_pic_url = self.__manage_friend_tech_user(shares_subject)
                        try:
                            twitter_user_data = self.tweepy_client.get_user(screen_name=twitter_username)
                            if twitter_user_data.followers_count >= 100_000:
                                buy_price_after_fee = self.web3.from_wei(self.contract.functions.getBuyPriceAfterFee(shares_subject,1).call(), "ether")
                                shares_count = self.contract.functions.sharesSupply(shares_subject).call()
                                msg = f"TwitterName: {twitter_username}, Followers: {twitter_user_data.followers_count}, Following: {twitter_user_data.friends_count}, Buy Price: Ξ{buy_price_after_fee}, Total Shares: {shares_count}"
                                msg += f", Time: {self.__convert_to_central_time(block.timestamp)}"
                                print(msg)
                                twitter_userdata.append(msg)
                                notification_data.append({
                                    "msg": msg,
                                    "image_url": profile_pic_url,
                                    "twitter_name": twitter_username,
                                    "shares_count": shares_count
                                })
                            else:
                                print(f"Not enough followers: {twitter_username}")
                        except NotFound as e:
                            print(f"{twitter_username} not found")
                        except TweepyException as e:
                            if 63 in e.api_codes:
                                raise TwitterForbiddenException("403 forbidden from twitter client")
                            else:
                                raise e
                    except requests.Timeout:
                        print("timeout")
                    except requests.HTTPError as e:
                        print("error")
        return twitter_userdata, notification_data
            
    def run(self, block_hash):
        users, notification_data = self.__perform_block_actions(block_hash)
        for notification in notification_data:
            if notification["shares_count"] < 3:
                self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK_NEW_USER_GREATER_THAN_100K)
            else:
                self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK)
        if self.friend_tech_users_to_create:
            FriendTechUser.objects.bulk_create([friend_tech_user for _, friend_tech_user in self.friend_tech_users_to_create.items()])
        return users