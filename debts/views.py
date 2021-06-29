from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import TransactionModalForm
from django.contrib import messages


# check if a given user is super_user
def _super_user_test(user):
    return user.is_superuser


@login_required
@user_passes_test(_super_user_test, login_url='my-transactions/')
def home(request):

    # get the debtors group
    debtor_group = Group.objects.get(pk=1)

    # user-wise debts summary
    debtors = debtor_group.user_set.annotate(
        total_lent=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=1)), 0, output_field=FloatField()),
        total_received=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=2)), 0, output_field=FloatField()),
        total_balance=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=1)), 0, output_field=FloatField()) - Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=2)), 0, output_field=FloatField())
    ).order_by('first_name')

    # overall debt summary
    overall_summary = Transaction.objects.aggregate(
        grand_total_lent = Coalesce(Sum('amount', filter=Q(transaction_type_id=1)), 0, output_field=FloatField()),
        grand_total_received=Coalesce(Sum('amount', filter=Q(transaction_type_id=2)), 0, output_field=FloatField()),
        grand_total_balance=Coalesce(Sum('amount', filter=Q(transaction_type_id=1)), 0, output_field=FloatField()) - Coalesce(Sum('amount', filter=Q(transaction_type_id=2)), 0, output_field=FloatField())
    )

    context = {
        'debtors': debtors,
        'overall_summary': overall_summary
    }

    return render(request, 'debts/home.html', context)


# debtor (users) homepage to track their debt status
@login_required
def my_transactions(request):

    # current user and current user's transactions
    user = request.user
    user_transactions = user.transaction_set.all().order_by('-transaction_date')

    # overall summary of the current user
    overall_summary = user.transaction_set.aggregate(
        grand_total_lent=Coalesce(Sum('amount', filter=Q(transaction_type_id=1)), 0, output_field=FloatField()),
        grand_total_received=Coalesce(Sum('amount', filter=Q(transaction_type_id=2)), 0, output_field=FloatField()),
        grand_total_balance=Coalesce(Sum('amount', filter=Q(transaction_type_id=1)), 0,
                                     output_field=FloatField()) - Coalesce(
            Sum('amount', filter=Q(transaction_type_id=2)), 0, output_field=FloatField())
    )

    context = {
        'transactions': user_transactions,
        'overall_summary' : overall_summary,
        'current_user': user
    }

    return render(request, 'debts/my_transactions.html', context)


@login_required
@user_passes_test(_super_user_test, login_url='my-transactions/')
def user_transactions(request, username):

    # current user and current user's transactions
    user = User.objects.filter(username=username).first()
    user_transactions = user.transaction_set.all().order_by('-transaction_date')

    # overall summary of the current user
    overall_summary = user.transaction_set.aggregate(
        grand_total_lent=Coalesce(Sum('amount', filter=Q(transaction_type_id=1)), 0, output_field=FloatField()),
        grand_total_received=Coalesce(Sum('amount', filter=Q(transaction_type_id=2)), 0, output_field=FloatField()),
        grand_total_balance=Coalesce(Sum('amount', filter=Q(transaction_type_id=1)), 0,
                                     output_field=FloatField()) - Coalesce(
            Sum('amount', filter=Q(transaction_type_id=2)), 0, output_field=FloatField())
    )

    context = {
        'transactions': user_transactions,
        'overall_summary' : overall_summary,
        'current_user': user
    }

    return render(request, 'debts/my_transactions.html', context)


@login_required
@user_passes_test(_super_user_test, login_url='my-transactions/')
def transaction_processor(request, username=None, transaction_id=None):

    # if we are on edit transaction
    if transaction_id is not None:
        trx = get_object_or_404(Transaction, pk=transaction_id)
    else:
        trx = Transaction()

    form = TransactionModalForm(request.POST or None, instance=trx)
    
    if username is None:
        # get all the debtors for group transaction
        debtor_group = Group.objects.get(pk=1)
        debtors = debtor_group.user_set.all()
        transaction_mode = 'group'
    else:
        # single user transaction
        debtors = User.objects.filter(username=username).first()
        transaction_mode = 'single'

    if request.method == 'POST':
        # form = TransactionModalForm(request.POST)
        if form.is_valid():

            if request.POST.get('transaction_mode') == 'group':
                selected_debtors = request.POST.getlist('debtor_id')
                print(selected_debtors)
                total_amount = request.POST.get('amount')
                per_head = float(total_amount) / len(selected_debtors)

                for debtor in selected_debtors:
                    print(debtor)
                    trx = form.save(commit=False)
                    trx.pk = None
                    trx.entered_by = request.user
                    trx.debtor_id = debtor
                    trx.amount = per_head
                    trx.save()

            else:
                trx = form.save(commit=False)
                trx.entered_by = request.user
                trx.debtor_id = request.POST.get('debtor_id')
                trx.save()

            messages.success(request, 'Transaction saved successfully')
            return redirect('home')

    context = {
        'debtors': debtors,
        'transaction_mode': transaction_mode,
        'form': form
    }

    return render(request, 'debts/transaction_form.html', context)