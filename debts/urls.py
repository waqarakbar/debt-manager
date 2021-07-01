from django.urls import path
from .views import home, my_transactions, user_transactions, transaction_processor, text_to_db

urlpatterns = [
    path('', home, name='home'),

    path('my-transactions/', my_transactions, name='my-transaction'),
    path('user-transactions/<str:username>/', user_transactions, name='user-transaction'),

    path('transaction-processor/<str:username>/<int:transaction_id>/', transaction_processor, name='new-transaction'),
    path('transaction-processor/<str:username>/', transaction_processor, name='new-transaction'),
    path('transaction-processor/', transaction_processor, name='new-transaction'),

    path('text-db/', text_to_db, name='textdb')
]