from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction, TradeRoutes
from app_functions.request_functions import *
from django.db.models import Q
from accounts.models import BrokerAccounts
from instrument.models import Tickers


@csrf_exempt
def update_portfolio(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))

        try:
            portfolio = Portfolio.objects.get(id=request_data['id'])
            for key, value in request_data.items():
                setattr(portfolio, key, value)
            portfolio.save()
            return JsonResponse({'response': 'Portfolio is updated'}, safe=False)
        except:
            return JsonResponse({'response': 'Error during update'}, safe=False)


@csrf_exempt
def update_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        print('UPDATE TRANSACTIONS')
        print(request_body)

        account = BrokerAccounts.objects.get(id=6)

        # Broker Account
        # account = BrokerAccounts.objects.get(id=6)

        # # Market value calculation
        # base_market_value = round(float(request_body['quantity']) * float(request_body['price']) * float(request_body['fx_rate']), 5)
        # local_market_value = round(float(request_body['quantity']) * float(request_body['price']), 5)
        #
        # # Market value to request body
        # request_body['mv'] = base_market_value
        # request_body['local_mv'] = local_market_value
        #
        # cash_flow_multiplier = 1
        # if request_body['transaction_type'] == 'Purchase' or request_body['sec_group'] == 'CFD':
        #     cash_flow_multiplier = -1
        #
        # # Linked Transaction update
        # if request_body['transaction_link_code'] != 0:
        #     main_transaction = Transaction.objects.get(id=request_body['transaction_link_code'])
        #     transaction_weight = abs(float(request_body['quantity']) / float(main_transaction.quantity))
        #
        #     if main_transaction.transaction_type == 'Purchase':
        #         pnl = round(float(request_body['quantity']) * (float(request_body['price']) - float(main_transaction.price)), 5)
        #     else:
        #         pnl = round(float(request_body['quantity']) * (float(main_transaction.price) - float(request_body['price'])), 5)
        #
        #     request_body['realized_pnl'] = pnl * float(request_body['fx_rate'])
        #     request_body['local_pnl'] = pnl
        #
        #     if main_transaction.sec_group == 'CFD':
        #         cash_flow = round((transaction_weight * main_transaction.net_cashflow * cash_flow_multiplier) + pnl, 5)
        #         request_body['net_cashflow'] = cash_flow * float(request_body['fx_rate'])
        #         request_body['local_cashflow'] = cash_flow
        #     else:
        #         request_body['net_cashflow'] = base_market_value * cash_flow_multiplier
        #         request_body['local_cashflow'] = local_market_value * cash_flow_multiplier
        #
        #     # if main_transaction.transaction_type == 'Purchase' or main_transaction.sec_group == 'CFD':
        #     #     if main_transaction.transaction_type == 'Purchase':
        #     #         pnl = round(float(request_body['quantity']) * (float(request_body['price']) - float(main_transaction.price)), 5)
        #     #     else:
        #     #         pnl = round(float(request_body['quantity']) * (float(main_transaction.price) - float(request_body['price'])), 5)
        #     #     net_cf = round((transaction_weight * main_transaction.net_cashflow * -1) + pnl, 5)
        #     #     margin_balance = round(transaction_weight * main_transaction.margin_balance * -1, 5)
        #     # else:
        #     #     pnl = round(float(request_body['quantity']) * (float(main_transaction.price) - float(request_body['price'])), 5)
        #     #     request_body['realized_pnl'] = pnl * request_body['fx_rate']
        #     #     request_body['local_pnl'] = pnl * request_body['fx_rate']
        #     #
        #     #     net_cf = round((transaction_weight * main_transaction.net_cashflow * -1) + pnl, 5)
        #     #     margin_balance = round(transaction_weight * main_transaction.margin_balance, 5)
        # else:
        #     if request_body['sec_group'] == 'CFD':
        #         ticker = Tickers.objects.get(inst_code=request_body['security'], source=account.broker_name)
        #         request_body['margin'] = ticker.margin
        #         request_body['net_cashflow'] = round(
        #             float(request_body['quantity']) * float(request_body['price']) * ticker.margin * float(
        #                 request_body['fx_rate']), 5) * cash_flow_multiplier
        #         request_body['local_cashflow'] = round(
        #             float(request_body['quantity']) * float(request_body['price']) * ticker.margin, 5) * cash_flow_multiplier
        #         request_body['margin_balance'] = round(
        #             float(request_body['quantity']) * float(request_body['price']) * (1 - ticker.margin), 5)
        #     else:
        #         request_body['net_cashflow'] = base_market_value * cash_flow_multiplier
        #         request_body['local_cashflow'] = local_market_value * cash_flow_multiplier
        #
        # dynamic_model_update(table_object=Transaction,
        #                      request_object=request_body)

        return JsonResponse({'response': 'Transaction is updated'}, safe=False)


@csrf_exempt
def update_trade_routing(request):
    if request.method == "POST":
        print('UPDATE TRADE ROUTING')
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        trade_route = TradeRoutes.objects.get(id=request_body['id'])
        trade_route.is_active = request_body['is_active']
        trade_route.quantity = request_body['quantity']
        trade_route.broker_account_id = request_body['broker_account_id']
        trade_route.save()

        return JsonResponse({'response': 'Transaction is closed'}, safe=False)



