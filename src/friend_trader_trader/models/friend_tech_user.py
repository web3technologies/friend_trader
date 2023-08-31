from django.db import models


class FriendTechUser(models.Model):
    
    address = models.CharField(max_length=255, unique=True)
    
    twitter_username = models.CharField(max_length=255, null=True, default=None)
    twitter_profile_pic = models.CharField(max_length=255, null=True, default=None)
    twitter_followers = models.IntegerField(null=True, default=None)

    current_price = models.DecimalField(null=True, default=None, decimal_places=25, max_digits=40)
    share_count = models.IntegerField(null=True, default=None)
    