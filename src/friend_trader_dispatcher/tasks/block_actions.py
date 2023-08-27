import json
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friend_trader.settings')
from django.conf import settings

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
        
    
    def __perform_block_actions(self, block_hash):
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
                        twitter_username = res.json().get("twitterUsername")
                        try:
                            twitter_user_data = self.tweepy_client.get_user(screen_name=twitter_username)
                            print(f"{twitter_username}: {twitter_user_data.followers_count} followers, following: {twitter_user_data.friends_count}")
                            buy_price_after_fee = self.web3.from_wei(self.contract.functions.getBuyPriceAfterFee(shares_subject,1).call(), "ether")
                            print(f"Buy Price: {buy_price_after_fee}")
                            print(f"Total Shares: {self.contract.functions.sharesSupply(shares_subject).call()}")
                        except NotFound as e:
                            print(f"{twitter_username} not found")
                    except requests.Timeout:
                        print("timeout")
                    except requests.HTTPError:
                        print("error")
        return block_hash
                        
    def run(self, block_hash):
        return self.__perform_block_actions(block_hash)