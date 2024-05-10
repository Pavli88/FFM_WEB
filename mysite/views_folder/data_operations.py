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
        csv_file = pd.read_csv(request.FILES['file'])

        for index, row in csv_file.iterrows():
            try:
                transaction = Transaction.objects.get(id=row['id'])
                transaction.portfolio_code = row['portfolio_code']
                transaction.quantity = row['quantity']
                transaction.price = row['price']
                transaction.mv = row['mv'],
                transaction.currency = row['currency'],
                transaction.trading_cost = row['trading_cost'],
                transaction.transaction_type = row['transaction_type'],
                transaction.transaction_link_code = row['transaction_link_code'],
                transaction.created_on = row['created_on']
                transaction.trade_date = row['trade_date'],
                transaction.is_active = row['is_active'],
                transaction.security = row['security'],
                transaction.sec_group = row['sec_group'],
                transaction.open_status = row['open_status'],
                transaction.broker_id = row['broker_id'],
                transaction.account_id = row['account_id'],
                transaction.margin = row['margin'],
                transaction.margin_balance = row['margin_balance'],
                transaction.net_cashflow = row['net_cashflow'],
                transaction.realized_pnl = row['realized_pnl'],
                transaction.option = row['option'],
                transaction.financing_cost = row['financing_cost'],
                transaction.local_cashflow = row['local_cashflow'],
                transaction.local_mv = row['local_mv'],
                transaction.local_pnl = row['local_pnl'],
                transaction.fx_pnl = row['fx_pnl'],
                transaction.fx_rate = row['fx_rate'],
                transaction.save()
            except:
                Transaction(
                    id=row['id'],
                    portfolio_code = row['portfolio_code'],
                quantity = row['quantity'],
                price = row['price'],
                mv = row['mv'],
                currency = row['currency'],
                trading_cost = row['trading_cost'],
                transaction_type = row['transaction_type'],
                transaction_link_code = row['transaction_link_code'],
                created_on = row['created_on'],
                trade_date = row['trade_date'],
                is_active = row['is_active'],
                security = row['security'],
                sec_group = row['sec_group'],
                open_status = row['open_status'],
                broker_id = row['broker_id'],
                account_id = row['account_id'],
                margin = row['margin'],
                margin_balance = row['margin_balance'],
                net_cashflow = row['net_cashflow'],
                realized_pnl = row['realized_pnl'],
                option = row['option'],
                financing_cost = row['financing_cost'],
                local_cashflow = row['local_cashflow'],
                local_mv = row['local_mv'],
                local_pnl = row['local_pnl'],
                fx_pnl = row['fx_pnl'],
                fx_rate = row['fx_rate'],
                ).save()

        response = {'response': 'Data is loaded'}
        return JsonResponse(response, safe=False)