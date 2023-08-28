

from django.conf import settings
import datetime
import json
import pytz
import requests
import tweepy
from tweepy.errors import NotFound
from web3 import Web3


class BlockActions:
    blast_wss = f"wss://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    CONTRACT_ADDRESS = "0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4"
    KOSSETTO_URL = "https://prod-api.kosetto.com/users"
    
    def __init__(self) -> None:
        twitter_auth = tweepy.OAuth1UserHandler(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.tweepy_client = tweepy.API(twitter_auth)
        self.web3 = Web3(Web3.WebsocketProvider(self.blast_wss))
        with open(settings.BASE_DIR / "src" / "web_socket_manager" / "abi.json", "r") as abis:
            contract_abis = json.loads(abis.read())
        self.contract = self.web3.eth.contract(address=self.CONTRACT_ADDRESS, abi=contract_abis)
        
    def __send_discord_messages(self, notification_data):
        for notification in notification_data:
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
            response = requests.post(settings.DISCORD_WEBHOOK, json=payload)
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
        
    
    def __perform_block_actions(self, block_hash):
        twitter_userdata, notification_data = [], []
        web3 = Web3(Web3.WebsocketProvider(self.blast_wss))
        block = web3.eth.get_block(block_hash, full_transactions=True)
        print(f"Block # {block.number}")
        for tx in block.transactions:
            if tx["to"] == self.contract.address:
                function, function_input = self.contract.decode_function_input(tx.input)
                if function.function_identifier == "buyShares":
                    try:
                        shares_subject = function_input.get('sharesSubject')
                        res = requests.get(f"{self.KOSSETTO_URL}/{shares_subject}", timeout=3)
                        res.raise_for_status()
                        kossetto_data = res.json()
                        twitter_username = kossetto_data.get("twitterUsername")
                        try:
                            twitter_user_data = self.tweepy_client.get_user(screen_name=twitter_username)
                            buy_price_after_fee = self.web3.from_wei(self.contract.functions.getBuyPriceAfterFee(shares_subject,1).call(), "ether")
                            msg = f"TwitterName: {twitter_username}, Followers: {twitter_user_data.followers_count}, Following: {twitter_user_data.friends_count}, Buy Price: Ξ{buy_price_after_fee}, Total Shares: {self.contract.functions.sharesSupply(shares_subject).call()}"
                            msg += f", Time: {self.__convert_to_central_time(block.timestamp)}"
                            print(msg)
                            twitter_userdata.append(msg)
                            if twitter_user_data.followers_count >= 300_000:
                                notification_data.append({
                                    "msg": msg,
                                    "image_url": kossetto_data.get("twitterPfpUrl"),
                                    "twitter_name": twitter_username
                                })
                        except NotFound as e:
                            print(f"{twitter_username} not found")
                    except requests.Timeout:
                        print("timeout")
                    except requests.HTTPError:
                        print("error")
        return twitter_userdata, notification_data
    
                        
    def run(self, block_hash):
        users, notification_data = self.__perform_block_actions(block_hash)
        if notification_data:
            self.__send_discord_messages(notification_data)
        return users