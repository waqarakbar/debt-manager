from django.urls import path
from .views import home, my_transactions, user_transactions, new_transaction

urlpatterns = [
    path('', home, name='home'),
    path('my-transactions/', my_transactions, name='my-transaction'),
    path('user-transactions/<str:username>/', user_transactions, name='user-transaction'),
    path('new-transaction/', new_transaction, name='new-transaction'),
    path('new-transaction/<str:username>/', new_transaction, name='new-transaction')
]