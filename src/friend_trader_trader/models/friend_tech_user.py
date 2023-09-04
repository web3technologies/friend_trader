from django.db import models

from friend_trader_core.clients import kossetto_client
from requests import Timeout


class FriendTechUser(models.Model):
    
    address = models.CharField(max_length=255, unique=True)
    
    twitter_username = models.CharField(max_length=255, null=True, default=None)
    twitter_profile_pic = models.CharField(max_length=255, null=True, default=None)
    twitter_followers = models.IntegerField(null=True, default=None)
    shares_supply = models.IntegerField(null=True, default=None)
    last_online = models.BigIntegerField(null=True, default=None)
    
    def __str__(self) -> str:
        return self.twitter_username


    def get_kossetto_data(self, auto_save=True):
        try:
            kossetto_data = kossetto_client.get_kossetto_user(address=self.address)
            twitter_username = kossetto_data.get("twitterUsername")
            profile_pic_url = kossetto_data.get("twitterPfpUrl")
            last_online = kossetto_data.get("lastOnline")
            self.twitter_username=twitter_username
            self.twitter_profile_pic=profile_pic_url
            self.last_online = last_online
            if auto_save:
                self.save(update_fields=["twitter_username", "twitter_profile_pic", "last_online"])
            return self
        except Timeout as e:
            print("handle timeout logic")
            
    def get_contract_data(self, contract, block_number, auto_save=True):
        shares_supply = contract.functions.sharesSupply(self.address).call()
        self.share_supply = shares_supply
        buy_price = contract.functions.getBuyPrice(self.address, 1).call(block_identifier=block_number)
        if shares_supply > 0:
            sell_price = contract.functions.getSellPrice(self.address, 1).call(block_identifier=block_number)
        if auto_save:
            self.save(update_fields=["shares_supply"])
        return self, buy_price, sell_price
        