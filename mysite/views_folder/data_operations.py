import json
import pandas as pd
from portfolio.models import Transaction
from instrument.models import Prices
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from instrument.instrument_pricing.oanda_pricing import oanda_pricing
from instrument.models import *
import csv


@csrf_exempt
def data_import(request):
    if request.method == "POST":
        print('DATA IMPORT')
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'})

        file = pd.read_csv(request.FILES['file'])
        process = request.POST.get('process')

        print(process)

        if process == 'transaction':
            transaction_import(file=file)

            return JsonResponse({'success': True})

        response = {'response': 'Data is loaded'}
        return JsonResponse(response, safe=False)


def transaction_import(file):
    print('TRANSACTION IMPORT')
    parent_transactions = file[file['parent'] == file['transaction_link_code']]
    child_transactions = file[file['parent'] != file['transaction_link_code']]

    print(parent_transactions)

    for index, row in parent_transactions.iterrows():
        print('PARENT ID:', row['parent'])

        # Creating parent transaction
        parent_transaction = Transaction.objects.create(
            portfolio_code=row['portfolio_code'],
            security_id=row['security'],
            quantity=row['quantity'],
            price=row['price'],
            trade_date=row['trade_date'],
            is_active=row['is_active'],
            transaction_type=row['transaction_type'],
            open_status='Open',
            account_id=row['account_id'] if pd.notnull(row['account_id']) else None,
            broker_id=row['broker_id'] if pd.notnull(row['broker_id']) else None,
            broker=row['broker'],
            fx_rate=row['fx_rate']
        )
        children = child_transactions[child_transactions['transaction_link_code'] == row['parent']]
        print('CHILDS')
        print(parent_transaction.id)
        print(children)
        # Creating child transactions
        for i, child in children.iterrows():
            Transaction.objects.create(
                portfolio_code=child['portfolio_code'],
                security_id=child['security'],
                quantity=child['quantity'],
                price=child['price'],
                trade_date=child['trade_date'],
                is_active=child['is_active'],
                transaction_type=child['transaction_type'],
                transaction_link_code=parent_transaction.id,
                open_status='Close',
                account_id=child['account_id'] if pd.notnull(child['account_id']) else None,
                broker_id=child['broker_id'] if pd.notnull(child['broker_id']) else None,
                broker=child['broker'],
                fx_rate=child['fx_rate']
            )

    # print(file)
def price_import():
    print('PRICE IMPORT')

def fx_import():
    print('FX IMPORT')

def instrument_import():
    print('INSTRUMENT IMPORT')

def nav_import():
    print('NAV IMPORT')