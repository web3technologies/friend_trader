from django.db import models

from friend_trader_trader.models import Trade


class Price(models.Model):
    
    price = models.DecimalField(max_digits=45, decimal_places=20)
    
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="prices")