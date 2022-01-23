from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('Query_Results.html', views.Query_Results, name='Query_Results'),
    path('Add_Transaction.html', views.Add_Transaction, name='Add_Transaction'),
    path('Buy_Stocks.html', views.Buy_Stocks, name='Buy_Stocks'),
    path('home.html', views.home, name='home')
]
