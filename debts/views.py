from django.shortcuts import render
from .models import Transaction
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required, user_passes_test


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
        'overall_summary' : overall_summary
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

