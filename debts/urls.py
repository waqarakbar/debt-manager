from django.urls import path
from .views import home, my_transactions, user_transactions

urlpatterns = [
    path('', home, name='home'),
    path('my-transactions/', my_transactions, name='my-transaction'),
    path('user-transactions/<str:username>/', user_transactions, name='user-transaction')
]