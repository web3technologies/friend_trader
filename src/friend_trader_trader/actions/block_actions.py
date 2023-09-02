import datetime
import json
import pytz
import random
import requests
import tweepy
from tweepy.errors import NotFound as TwitterUserNotFound, TweepyException
from web3 import Web3
from celery.exceptions import MaxRetriesExceededError

from django.conf import settings
from django.utils import timezone

from friend_trader_core.clients import kossetto_client
from friend_trader_trader.models import Block, FriendTechUser, SharePrice, Transaction
from friend_trader_trader.exceptions.exceptions import TwitterForbiddenException


class BlockActions:
    blast_url = f"https://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    ankr_url = "https://rpc.ankr.com/base"
    CONTRACT_ADDRESS = "0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4"

    with open(settings.BASE_DIR / "src" / "web_socket_manager" / "abi.json", "r") as abis:
        contract_abis = json.loads(abis.read())

    twitter_auth = tweepy.OAuth1UserHandler(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
    tweepy_client = tweepy.API(twitter_auth)
    web3_providers = [
            # Web3(Web3.HTTPProvider(ankr_url)),
            Web3(Web3.HTTPProvider(blast_url))
        ]
    
    def __init__(self, task, block_number=None, send_notifications=False) -> None:
        self.task = task
        self.send_notifications = send_notifications
        self.block_number =  block_number
        self.block = Block.objects.get_or_create(block_number=block_number)[0]
        self.web3 = random.choice(self.web3_providers)
        self.contract = self.web3.eth.contract(address=self.CONTRACT_ADDRESS, abi=self.contract_abis)
        self.friend_tech_users_to_create = []
        self.friend_tech_user_addresses = []
        self.twitter_userdata = []
        self.notification_data =  []
        self.transcations_to_create = []
        self.share_prices_to_create = []

        
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
            if not friend_tech_user.twitter_username:
                friend_tech_user.get_kossetto_data(auto_save=True)
        except FriendTechUser.DoesNotExist:
            if shares_subject not in self.friend_tech_user_addresses:
                friend_tech_user = FriendTechUser(address=shares_subject)
                friend_tech_user.get_kossetto_data(auto_save=False)
                self.friend_tech_users_to_create.append(friend_tech_user)
                self.friend_tech_user_addresses.append(shares_subject)
            
        return friend_tech_user
    
    def __manage_twitter_user(self, twitter_username):
        try:
            twitter_user_data = self.tweepy_client.get_user(screen_name=twitter_username)
            return twitter_user_data
        except TwitterUserNotFound as e:
            print(f"{twitter_username} not found")
        except TweepyException as e:
            if 63 in e.api_codes:
                raise TwitterForbiddenException("403 forbidden from twitter client")
            else:
                raise e
            
    def __manage_twitter_user_data(self, block, shares_subject, twitter_user_data, twitter_username, profile_pic_url):
        if twitter_user_data.followers_count >= 100_000:
            buy_price_after_fee = self.web3.from_wei(self.contract.functions.getBuyPriceAfterFee(shares_subject,1).call(), "ether")
            shares_count = self.contract.functions.sharesSupply(shares_subject).call()
            msg = f"TwitterName: {twitter_username}, Followers: {twitter_user_data.followers_count}, Following: {twitter_user_data.friends_count}, Buy Price: Ξ{buy_price_after_fee}, Total Shares: {shares_count}"
            msg += f", Time: {self.__convert_to_central_time(block.timestamp)}"
            print(msg)
            self.twitter_userdata.append(msg)
            self.notification_data.append({
                "msg": msg,
                "image_url": profile_pic_url,
                "twitter_name": twitter_username,
                "shares_count": shares_count
            })
        else:
            print(f"Not enough followers: {twitter_username}")
        
    def __perform_block_actions(self):
        fetched_block = self.web3.eth.get_block(self.block_number, full_transactions=True)
        self.block.block_timestamp = fetched_block.timestamp
        self.block.block_hash = fetched_block.hash
        self.block.save(update_fields=["block_timestamp", "block_hash"])
        print(f"Block # {fetched_block.number}")
        for tx in fetched_block.transactions:
            if tx["to"] == self.contract.address:
                function, function_input = self.contract.decode_function_input(tx.input)
                if function.function_identifier == "buyShares":
                    shares_subject = function_input.get('sharesSubject')
                    friend_tech_user = self.__manage_friend_tech_user(shares_subject)
                    twitter_user_data = self.__manage_twitter_user(friend_tech_user.twitter_username)
                    if twitter_user_data:
                        self.__manage_twitter_user_data(fetched_block, shares_subject, twitter_user_data, friend_tech_user.twitter_username, friend_tech_user.twitter_profile_pic)
                    else:
                        print("no twitter user data")
                    # self.transcations_to_create.append(
                    #     Transaction(
                    #         type="BUY",
                    #         price=tx["value"],
                    #         seller=friend_tech_user,
                    #         buyer=FriendTechUser.objects.get(address=tx["from"]),
                    #         block=self.block
                    #     )
                    # )
                elif function.function_identifier == "sellShares":
                    pass
                else:
                    pass
    
    def __handle_notifications(self):
        if self.send_notifications:
            for notification in self.notification_data:
                if notification["shares_count"] < 3:
                    self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK_NEW_USER_GREATER_THAN_100K)
                else:
                    self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK)

    def __handle_post_processing_db_updates(self):
        FriendTechUser.objects.bulk_create(self.friend_tech_users_to_create)
        if self.transcations_to_create:
            Transaction.objects.bulk_create(self.transcations_to_create)
        if self.share_prices_to_create:
            SharePrice.objets.bulk_create(self.share_prices_to_create)
        self.block.date_sniffed = timezone.now()
        self.block.save(update_fields=["date_sniffed"])
    
    def run(self):
        self.__perform_block_actions()
        self.__handle_notifications()
        self.__handle_post_processing_db_updates()