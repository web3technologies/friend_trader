from django.db import models


class Block(models.Model):
    block_hash = models.CharField(max_length=255, null=True, default=None)
    block_number = models.IntegerField(null=True, default=None)
    block_timestamp = models.BigIntegerField(null=True, default=None)
    date_sniffed = models.DateTimeField(null=True, default=None)
