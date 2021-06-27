from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class TransactionType(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.title}'

class Transaction(models.Model):
    debtor = models.ForeignKey(User, on_delete=models.CASCADE)
    entered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entered_by')
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    amount = models.FloatField()
    remarks = models.TextField(blank=True)
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.debtor.username}: amount ({self.amount}): transaction_type ({self.transaction_type.title}): dated ({self.transaction_date})'

    def absolute_url(self):
        pass
