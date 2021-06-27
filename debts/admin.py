from django.contrib import admin
from .models import TransactionType, Transaction

admin.site.register(TransactionType)
admin.site.register(Transaction)
