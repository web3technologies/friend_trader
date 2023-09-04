import datetime
import json
import pytz
import random
import requests
import tweepy
from tweepy.errors import NotFound as TwitterUserNotFound, TweepyException
from web3 import Web3

from django.conf import settings
from django.utils import timezone

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
        self.block_number = block_number
        self.block = Block.objects.get_or_create(block_number=block_number)[0]
        self.web3 = random.choice(self.web3_providers)
        self.contract = self.web3.eth.contract(address=self.CONTRACT_ADDRESS, abi=self.contract_abis)
        self.twitter_userdata = []
        self.notification_data =  []
        self.transcations_to_create = []
        self.share_prices_to_create = []
        
    @property
    def function_handler(self):
        return {
            "buyShares": self.__buy_or_sell_shares,
            "sellShares": self.__buy_or_sell_shares
        }

        
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
            friend_tech_user = FriendTechUser.objects.create(address=shares_subject)
            try:
                friend_tech_user.get_kossetto_data(auto_save=True)
            except requests.exceptions.HTTPError:
                print("Error fetching data")
        except requests.exceptions.HTTPError:
            print("Error fetching data")
            
        return friend_tech_user
            
    def __manage_share_price(self, friend_tech_user: FriendTechUser) -> SharePrice:
        friend_tech_user, buy_price, sell_price = friend_tech_user.get_contract_data(self.contract, self.block_number)
        share_price_obj = SharePrice(
              buy_price=self.web3.from_wei(buy_price, "ether") if buy_price else None,
              sell_price=self.web3.from_wei(sell_price, "ether") if sell_price else None,
              block=self.block,
              friend_tech_user=friend_tech_user
            )
        self.share_prices_to_create.append(share_price_obj)
        return friend_tech_user
            
    def __manage_twitter_user_data(self, friend_tech_user):
        try:
            twitter_user_data = self.tweepy_client.get_user(screen_name=friend_tech_user.twitter_username)
            if twitter_user_data.followers_count >= 100_000:
                buy_price_after_fee = self.web3.from_wei(self.contract.functions.getBuyPriceAfterFee(friend_tech_user.address,1).call(), "ether")
                msg = f"TwitterName: {friend_tech_user.twitter_username}, Followers: {twitter_user_data.followers_count}, Following: {twitter_user_data.friends_count}, Buy Price: Ξ{buy_price_after_fee}, Total Shares: {friend_tech_user.shares_supply}"
                msg += f", Time: {self.__convert_to_central_time(self.block.block_timestamp)}"
                print(msg)
                self.twitter_userdata.append(msg)
                self.notification_data.append({
                    "msg": msg,
                    "image_url": friend_tech_user.twitter_profile_pic,
                    "twitter_name": friend_tech_user.twitter_username,
                    "shares_count": friend_tech_user.shares_supply
                })
            else:
                print(f"Not enough followers: {friend_tech_user.twitter_username}")
        except TwitterUserNotFound as e:
            print(f"{friend_tech_user.twitter_username} not found")
        except TweepyException as e:
            if 63 in e.api_codes:
                raise TwitterForbiddenException("403 forbidden from twitter client")
            else:
                raise e
        
    def __buy_or_sell_shares(self, function, function_input, tx):
        shares_subject = function_input.get('sharesSubject')
        friend_tech_user = self.__manage_friend_tech_user(shares_subject)
        friend_tech_user = self.__manage_share_price(friend_tech_user)
        self.__manage_twitter_user_data(friend_tech_user)
        self.transcations_to_create.append(
            Transaction(
                type=function.function_identifier,
                price=tx["value"],
                seller=friend_tech_user,
                buyer=FriendTechUser.objects.get_or_create(address=tx["from"])[0],
                block=self.block,
                transaction_hash=tx.hash.hex()
            )
        )
        
    def __perform_block_actions(self):
        fetched_block = self.web3.eth.get_block(self.block_number, full_transactions=True)
        self.block.block_timestamp = fetched_block.timestamp
        self.block.block_hash = fetched_block.hash
        self.block.save(update_fields=["block_timestamp", "block_hash"])
        print(f"Block # {fetched_block.number}")
        for tx in fetched_block.transactions:
            if tx["to"] == self.contract.address:
                function, function_input = self.contract.decode_function_input(tx.input)
                if function.function_identifier in self.function_handler:
                    self.function_handler[function.function_identifier](function, function_input, tx)
    
    def __handle_notifications(self):
        if self.send_notifications:
            for notification in self.notification_data:
                if notification["shares_count"] < 3:
                    self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK_NEW_USER_GREATER_THAN_100K)
                else:
                    self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK)

    def __handle_post_processing_db_updates(self):
        if self.transcations_to_create:
            Transaction.objects.bulk_create(self.transcations_to_create)
        if self.share_prices_to_create:
            SharePrice.objects.bulk_create(self.share_prices_to_create)
        self.block.date_sniffed = timezone.now()
        self.block.save(update_fields=["date_sniffed"])
    
    def run(self):
        self.__perform_block_actions()
        self.__handle_notifications()
        self.__handle_post_processing_db_updates()