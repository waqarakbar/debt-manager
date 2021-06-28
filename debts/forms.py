from django import forms
from django.forms import ModelForm
from .models import Transaction


class TransactionCreationForm(forms.Form):
    CHOICES = [('1', 'Lent'), ('2', 'Recovered')]

    transaction_type_id = forms.CharField(label='Transaction Type', widget=forms.RadioSelect(choices=CHOICES), initial=1)
    amount = forms.FloatField(label='Total Amount')
    remarks = forms.CharField(label='Remarks', widget=forms.Textarea)