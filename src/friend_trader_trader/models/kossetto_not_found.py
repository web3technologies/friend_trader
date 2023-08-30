from django.db import models
from django.utils import timezone


class KossettoNotFound(models.Model):
    address = models.CharField(max_length=255, unique=True)
    date_created = models.DateTimeField(default=timezone.now)
    blockhash = models.CharField(max_length=255)