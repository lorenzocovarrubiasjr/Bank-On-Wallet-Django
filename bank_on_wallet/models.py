from django.db import models
import requests 
from random import *
import hashlib 

class Account(models.Model):
    account_num = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    pass_hash = models.CharField(max_length=64)
    salt = models.CharField(default="",max_length=30)
    balance = models.FloatField(default=0)
    
    def gen_account_num(self):
        self.account_num = "".join([str(randint(0,9)) for _ in range(16)])

    def salt_and_hasher(self, password):
        salt = "".join([chr(randint(36,126)) for _ in range(10)])
        sap = (salt + password).encode("utf-8")
        self.pass_hash = hashlib.sha256(sap).hexdigest()
        self.salt = salt
        
    def portfolio_value(self):
        positions = Position.objects.filter(account = self.id)
        portfolio_value = 0.00
        for position in positions:
            resp = requests.get("https://api.iextrading.com/1.0/tops/last", params={"symbols": position.symbol})
            price = resp.json()[0]["price"]
            cost = round((position.quantity) * price, 2) 
            portfolio_value += cost 
        portfolio_value = round(portfolio_value, 2)
        return portfolio_value
    
class Position(models.Model):
    symbol = models.CharField(max_length=12)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    quantity = models.FloatField()

    
    def current_price(self):
        resp = requests.get("https://api.iextrading.com/1.0/tops/last", params={"symbols": self.symbol})
        price = resp.json()[0]["price"]
        price = round(price, 2) 
        self.loaded_price = price
        return price
    
    def current_value(self):
        return self.quantity * self.loaded_price
    
class Trade(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    time_of_trade = models.DateTimeField(auto_now_add=True)
    symbol = models.CharField(max_length=12)
    quantity = models.FloatField()
    buy_or_sell = models.CharField(max_length=12)
    cost = models.FloatField(default=0.00)
    