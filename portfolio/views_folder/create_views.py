import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Robots, Portfolio, CashFlow, Transaction
from instrument.models import Instruments, Tickers, Prices
from accounts.models import BrokerAccounts
import json
from app_functions.request_functions import *
from app_functions.calculations import *


@csrf_exempt
def create_robot(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        if Robots.objects.filter(portfolio_code=request_data['portfolio_code'],
                                 inst_id=request_data['inst_id']).exists():
            return JsonResponse({'response': 'Security is already mapped to this portfolio'}, safe=False)
        else:
            Robots(portfolio_code=request_data['portfolio_code'],
                   inst_id=request_data['inst_id'],
                   ticker_id=request_data['ticker_id'],
                   broker_account_id=request_data['broker_account_id']).save()
            return JsonResponse({'response': 'Security mapping is completed'}, safe=False)


@csrf_exempt
def create_portfolio(request):
    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        try:
            port = Portfolio(portfolio_name=body_data["port_name"],
                             portfolio_code=body_data["port_code"],
                             portfolio_type=body_data["port_type"],
                             currency=body_data["port_currency"],
                             status="active",
                             inception_date=body_data["inception_date"],
                             owner=body_data["owner"])
            port.save()
            return JsonResponse({'msg': "New Portfolio is created!", 'port': port.id}, safe=False)
        except:
            return JsonResponse({'msg': "Portfolio exists in database!", 'port': 0}, safe=False)


@csrf_exempt
def create_cashflow(request):
    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        try:
            CashFlow(
                portfolio_code=body_data['portfolio_code'],
                amount=body_data['amount'],
                type=body_data['type'],
                date=body_data['date'],
                user=body_data['user'],
                currency=body_data['currency']
            ).save()
        except:
            print('Error in cash insert')
        return JsonResponse({"msg": "Cashflow entered into database!"}, safe=False)


@csrf_exempt
def create_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)

        # Cash Transaction
        if request_body['sec_group'] == 'Cash':
            dynamic_model_create(table_object=Transaction(),
                                 request_object=request_body)
            return JsonResponse({"response": "Cash transaction is created!"}, safe=False)
        account = BrokerAccounts.objects.get(id=6)
        ticker = Tickers.objects.get(inst_code=request_body['security'],
                                     source=account.broker_name)
        request_body['margin'] = ticker.margin

        # New transaction
        if request_body['transaction_link_code'] == '':
            # With margin
            if request_body['sec_group'] == 'CFD':
                if request_body['transaction_type'] == 'Purchase':
                    request_body['net_cashflow'] = float(request_body['quantity']) * float(request_body['price']) * ticker.margin * -1
                    request_body['margin_balance'] = float(request_body['quantity']) * float(
                        request_body['price']) * (1 - ticker.margin)
            # Without margin
            else:
                if request_body['transaction_type'] == 'Purchase':
                    request_body['net_cashflow'] = float(request_body['quantity']) * float(request_body['price']) * -1
                else:
                    request_body['net_cashflow'] = float(request_body['quantity']) * float(request_body['price'])
            dynamic_model_create(table_object=Transaction(),
                                 request_object=request_body)
        else:
            # Linked transaction
            main_transaction = Transaction.objects.get(id=request_body['transaction_link_code'])
            linked_transactions = pd.DataFrame(Transaction.objects.filter(transaction_link_code=request_body['transaction_link_code']).values())
            transaction_weight = abs(float(request_body['quantity']) / float(main_transaction.quantity))

            if main_transaction.transaction_type == 'Purchase':
                pnl = float(request_body['quantity']) * (
                        float(request_body['price']) - float(main_transaction.price))
                net_cf = (transaction_weight * main_transaction.net_cashflow * -1) + pnl
                margin_balance = transaction_weight * main_transaction.margin_balance * -1
            else:
                pnl = float(request_body['quantity']) * (float(main_transaction.price) - float(request_body['price']))
                net_cf = (transaction_weight * main_transaction.net_cashflow * -1) + pnl
                margin_balance = transaction_weight * main_transaction.margin_balance

            print('WEIGHT', transaction_weight)
            print('PNL', pnl)
            print('NET CF', (transaction_weight * main_transaction.net_cashflow) + pnl)

            request_body['realized_pnl'] = pnl
            request_body['net_cashflow'] = net_cf
            request_body['margin_balance'] = margin_balance

            dynamic_model_create(table_object=Transaction(),
                                 request_object=request_body)

            # if main_transaction.sec_group == 'CFD':
            #     if main_transaction.transaction_type == 'Purchase':

            #         # self.margin_balance = self.mv * (1 - float(self.margin))
            #     else:
            #         self.net_cashflow = self.mv * self.margin * -1
            #         self.margin_balance = self.mv * (1 - float(self.margin))
            # elif self.transaction_type == 'Purchase':
            #     self.net_cashflow = self.mv * -1
            # else:
            #     self.net_cashflow = self.mv

            # print(main_transaction.quantity)
            # print(linked_transactions['quantity'].sum())
            #
            #
            # if abs(float(main_transaction.quantity)) - abs(float(linked_transactions['quantity'].sum())) == 0.0:
            #     return JsonResponse({"response": "Transactions are offsetted. New linked transaction can not be added."}, safe=False)
            #
            # if abs(float(main_transaction.quantity)) - abs(float(linked_transactions['quantity'].sum())) - abs(
            #         float(request_body['quantity'])) < 0.0:
            #     return JsonResponse({"response": "Total offsetting ammount is greater than original trade quantity. New linked transaction can not be added."},
            #                         safe=False)
            #
            # if abs(float(main_transaction.quantity)) - abs(float(linked_transactions['quantity'].sum())) - abs(
            #         float(request_body['quantity'])) == 0.0:
            #     print('Last TRANSACTION')
            #     dynamic_model_create(table_object=Transaction(),
            #                          request_object=request_body)
            # else:
            #     dynamic_model_create(table_object=Transaction(),
            #                          request_object=request_body)

        try:
            price = Prices.objects.get(date=request_body['trade_date'], inst_code=request_body['security'])
            price.price = request_body['price']
            price.save()
        except Prices.DoesNotExist:
            Prices(inst_code=request_body['security'],
                   date=request_body['trade_date'],
                   price=request_body['price']).save()
        return JsonResponse({"response": "Transaction is created!"}, safe=False)


@csrf_exempt
def cash_holding_calculation(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        calculate_cash_holding(portfolio_code=request_body['portfolio_code'],
                               start_date=request_body['trade_date'],
                               currency=request_body['currency'])
        return JsonResponse({"response": "Transaction is created!"}, safe=False)


