from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('new_account/', views.new_account, name= 'new_account'),
    path('create_account/', views.create_account, name="create_account"),
    path('home/', views.home, name="home"),
    path('deposit/', views.deposit, name="deposit"),
    path('deposited/', views.deposited, name="deposited"),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('withdrawn/', views.withdrawn, name="withdrawn"),
    path('buy/', views.buy, name="buy"),
    path('bought/', views.bought, name="bought"),
    path('sell/', views.sell, name="sell"),
    path("sold/", views.sold, name="sold"),
    path("validate", views.validate, name="validate"),
    path('logout/', views.logout, name='logout')
]