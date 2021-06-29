from django import forms
from django.forms import ModelForm, RadioSelect, widgets
from .models import Transaction


class TransactionCreationForm(forms.Form):
    CHOICES = [('1', 'Lent'), ('2', 'Recovered')]

    transaction_type_id = forms.CharField(label='Transaction Type', widget=forms.RadioSelect(choices=CHOICES), initial=1)
    amount = forms.FloatField(label='Total Amount')
    # transaction_date = forms.DateField(label='Transaction Date', widget=forms.SelectDateWidget)
    remarks = forms.CharField(label='Remarks', widget=forms.Textarea, required=False)


class TransactionModalForm(ModelForm):

    class Meta:
        model = Transaction
        fields = ['transaction_date', 'transaction_type', 'amount', 'remarks']

        widgets = {
            'transaction_type': RadioSelect(),
            'transaction_date': widgets.DateInput(attrs={'type': 'date'})
        }