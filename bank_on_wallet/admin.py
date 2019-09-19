from django.contrib import admin
from .models import Account, Position, Trade

admin.site.register(Account)
admin.site.register(Position)
admin.site.register(Trade)

class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_num", "username", "name", "balance", "pass_hash")
    
class Position(admin.ModelAdmin):
    list_display = ("account", "symbol", "quantity")
    
class Trade(admin.ModelAdmin):
    list_display = ("buy_or_sell", "time_of_trade", "account", "symbol", "quantity")
