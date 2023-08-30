from django.db import models


class FriendTechUser(models.Model):
    
    address = models.CharField(max_length=255, unique=True)
    twitter_username = models.CharField(max_length=255, null=True, default=None)
    twitter_profile_pic = models.CharField(max_length=255, null=True, default=None)