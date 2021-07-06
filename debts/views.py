from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Transaction
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import TransactionModalForm
from django.contrib import messages
import csv
import datetime
import dropbox
import os
from django.conf import settings


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


@login_required
@user_passes_test(_super_user_test, login_url='my-transactions/')
def download_summary_csv(request):
    # get the debtors group
    debtor_group = Group.objects.get(pk=1)

    # user-wise debts summary
    debtors = debtor_group.user_set.annotate(
        total_lent=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=1)), 0, output_field=FloatField()),
        total_received=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=2)), 0, output_field=FloatField()),
        total_balance=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=1)), 0, output_field=FloatField()) -
                      Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=2)), 0, output_field=FloatField())
    ).order_by('first_name')

    date_now = datetime.datetime.now()
    filename = 'summary_'+date_now.strftime("%Y-%m-%d %H-%M-%S %f")+".csv"
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )

    writer = csv.writer(response)

    writer.writerow(['Name', 'Total Lent', 'Total Recovered', 'Balance'])

    for debtor in debtors:
        writer.writerow([
            debtor.first_name+" "+debtor.last_name+" @"+debtor.username,
            round(debtor.total_lent, 2),
            round(debtor.total_received, 2),
            round(debtor.total_balance, 2)
        ])

    return response


@login_required
@user_passes_test(_super_user_test, login_url='my-transactions/')
def sync_to_dropbox(request):

    access_token = settings.DBX_ACCESS_TOKEN

    # get debts summary
    debtor_group = Group.objects.get(pk=1)
    debtors = debtor_group.user_set.annotate(
        total_lent=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=1)), 0,
                            output_field=FloatField()),
        total_received=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=2)), 0,
                                output_field=FloatField()),
        total_balance=Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=1)), 0,
                               output_field=FloatField()) -
                      Coalesce(Sum('transaction__amount', filter=Q(transaction__transaction_type_id=2)), 0,
                               output_field=FloatField())
    ).order_by('first_name')

    # create a unique dated file name to be saved to dropbox
    date_now = datetime.datetime.now()
    filename = settings.IS_DUMMY+'summary_' + date_now.strftime("%Y-%m-%d %H-%M-%S %f") + ".csv"
    full_path = os.path.join(settings.MEDIA_ROOT+filename)

    row_list = []
    row_list.append(['Name', 'Total Lent', 'Total Recovered', 'Balance'])
    for debtor in debtors:
        row_list.append([
            debtor.first_name + " " + debtor.last_name + " @" + debtor.username,
            round(debtor.total_lent, 2),
            round(debtor.total_received, 2),
            round(debtor.total_balance, 2)
        ])

    # save csv file to media
    with open(full_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)


    # open file, save to dropbox and then delete it form media
    dbx = dropbox.Dropbox(access_token)
    with open(full_path, "rb") as f:
        try:
            dbx.files_upload(f.read(), '/'+filename, mute=True)
            os.remove(full_path)
            messages.success(request, 'Sync to dropbox')
        except:
            messages.error(request, 'Dropbox sync failed')

    return redirect('home')





# def text_to_db(request):
#
#     import os
#     from datetime import datetime
#
#     module_dir = os.path.dirname(__file__)
#     file_path = os.path.join(module_dir, 'static/zeeshan.txt')  # full path to text.
#     debtor_id = 21
#     data_file = open(file_path, 'r')
#     data = data_file.read()
#     data_list = data.splitlines()
#     # print(data_list)
#     for d in data_list:
#         this_date, amount = d.split(":")
#
#         ## transaction date
#         date_obj = datetime.strptime(this_date, "%d %B %Y")
#
#         amount_striped = amount.strip()
#
#         ## transaction type
#         sign = amount_striped[0]
#
#         if sign == '+':
#             # remove first 3 chars
#             without_unit = amount_striped[3:]
#             ttype = 1
#         else:
#             # remove first 4 chars
#             without_unit = amount_striped[3:]
#             ttype = 2
#
#         amount_remarks = without_unit.split(" (")
#
#         ## transaction amount
#         transaction_amount = float(amount_remarks[0].replace(",", "").strip())
#
#         comment = "";
#         if len(amount_remarks) > 1:
#             # we also have a transaction comment
#             comment = amount_remarks[1].strip().rstrip(")")
#
#         print("date: ", date_obj, " | type: ", sign, " | amount: ", transaction_amount, " | comment: ", comment)
#
#         trx = Transaction(
#             amount=transaction_amount,
#             remarks=comment,
#             transaction_date=date_obj,
#             created_at=date_obj,
#             debtor_id=debtor_id,
#             entered_by_id=1,
#             transaction_type_id=ttype
#         )
#         trx.save()
#
#
#
#     return HttpResponse('done')