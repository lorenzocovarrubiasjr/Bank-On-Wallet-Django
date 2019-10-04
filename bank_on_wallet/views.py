from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm 
from django.urls import reverse_lazy
from django.views import generic
import requests 
import hashlib 
import math
from .models import Account, Position, Trade

def index(request):
    return render(request,'bank_on_wallet/index.html')

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'bank_on_wallet/signup.html'

def validate(request):
    try:
        if request.method == "POST":
            post_dict = request.POST.dict()
            username = post_dict["username"]
            password = post_dict["password"]
            acct = Account.objects.get(username=username) 
            if acct.username == username:
                sap = (acct.salt + password).encode("utf-8")
                pass_hash = hashlib.sha256(sap).hexdigest()
                if acct.pass_hash == pass_hash:
                    context = {"account": acct}
                    request.session["acct_id"] = acct.id 
                    return render(request, 'bank_on_wallet/home.html', context)
                else:
                    return redirect("index")
            else:
                return redirect("index")
        else:
            return redirect("index")
    except:
        return redirect("index")
        
def new_account(request):
    return render(request, 'bank_on_wallet/new_account.html')

def create_account(request):
    if request.method != "POST":
        return redirect("new_account.html")
    try:
        name = request.POST["name"]
        username = request.POST["username"]
        password = request.POST["password"]
        acct = Account(name=name, username=username)
        acct.gen_account_num()
        acct.salt_and_hasher(password)
        print("Here is account info::::>>>",acct.name, " ",acct.balance," ", acct.username, " ", acct.account_num)
        acct.save()
        request.session["acct_id"] = acct.id 
        return redirect("index")
    except KeyError:
        return redirect("new_account")
    
def home(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("/bank_on_wallet/")
    acct = Account.objects.get(id=acct_id)
    acct_positions = Position.objects.filter(account_id = acct_id).order_by("-quantity")
    acct_trades = Trade.objects.filter(account = acct_id).order_by("-time_of_trade")
    portfolio_value = acct.portfolio_value() 
    context = {"account": acct, "positions": acct_positions, "trades": acct_trades, "portfolio_value": portfolio_value}
    return render(request, 'bank_on_wallet/home.html', context)

def deposit(request):
    acct_id = request.session.get("acct_id")
    print("Acct id::   ", acct_id)
    if not acct_id:
        return redirect("bank_on_wallet/index.html")
    acct = Account.objects.get(id=acct_id)
    portfolio_value = acct.portfolio_value() 
    context = {"account": acct, "portfolio_value": portfolio_value}
    return render(request, "bank_on_wallet/deposit.html", context)

def deposited(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("index.html")
    try:
        money = float(request.POST["money"])
        acct = Account.objects.get(id=acct_id)
        acct.balance += money 
        acct.balance = round(acct.balance, 2)
        acct.save()
        return redirect('home')
    except KeyError:
        return redirect('home')
    except ValueError:
        return redirect('home')
    
def withdraw(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("bank_on_wallet/index.html")
    acct = Account.objects.get(id=acct_id)
    portfolio_value = acct.portfolio_value() 
    context = {"account": acct, "portfolio_value": portfolio_value}
    return render(request, "bank_on_wallet/withdraw.html", context)

def withdrawn(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("login")
    try:
        money = float(request.POST["money"])
        acct = Account.objects.get(id=acct_id)
        acct.balance -= money 
        acct.balance = round(acct.balance, 2)
        acct.save()
        return redirect('home')
    except KeyError:
        return redirect('home')
    except ValueError:
        return redirect('home')
    
def buy(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("login")
    acct = Account.objects.get(id=acct_id)
    portfolio_value = acct.portfolio_value() 
    context = {"account": acct, "portfolio_value": portfolio_value}
    return render(request, "bank_on_wallet/buy.html", context)

def bought(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("index")
    acct = Account.objects.get(id=acct_id)
    symbol = request.POST["symbol"].upper()
    quantity = float(request.POST["qty"])
    resp = requests.get("https://api.iextrading.com/1.0/tops/last", params={"symbols": symbol})
    price = resp.json()[0]["price"]
    cost = round(quantity * price, 2) 
    if acct.balance < cost:
        return redirect("home")
    else:
        acct.balance -= cost
        acct.balance = round(acct.balance, 2)
        acct.save()
        trade = Trade(account=acct, symbol=symbol, quantity=quantity,buy_or_sell="BUY", cost=cost)
        trade.save()
        maybe_p = acct.position_set.filter(symbol=symbol)
        if len(maybe_p) > 0:
            position = maybe_p[0]
            position.quantity += quantity
            position.save()
        else:
            position = Position(symbol=symbol, account=acct, quantity=quantity)
            position.save()
    return redirect("home")

def sell(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("login")
    acct = Account.objects.get(id=acct_id)
    portfolio_value = acct.portfolio_value() 
    context = {"account": acct, "portfolio_value": portfolio_value}
    return render(request, "bank_on_wallet/sell.html", context)

def sold(request):
    acct_id = request.session.get("acct_id")
    if not acct_id:
        return redirect("bank_on_wallet/home.html")
    else:
        acct = Account.objects.get(id=acct_id)
        symbol = request.POST["symbol"].upper()
        quantity = float(request.POST["qty"])
        resp = requests.get("https://api.iextrading.com/1.0/tops/last", params={"symbols": symbol})
        price = resp.json()[0]["price"]
        cost = round(quantity * price, 2) 
        maybe_p = acct.position_set.filter(symbol=symbol)
        if len(maybe_p) > 0: 
            acct.balance += cost
            acct.balance = round(acct.balance, 2)
            acct.save()
            trade = Trade(account=acct, symbol=symbol, quantity=quantity,buy_or_sell="SELL", cost=cost)
            trade.save()
            position = maybe_p[0]
            position.quantity -= quantity
            position.save()
        else:
            return redirect("bank_on_wallet/home.html")
        return redirect("home")
    
def logout(request):
    request.session["acct_id"] = None 
    return redirect("index")
