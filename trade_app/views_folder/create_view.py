from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction, Nav, TradeRoutes
from trade_app.models import Notifications, Signal
import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from trade_app.services import TradeExecution
from trade_app.tasks import execute_trade_signal

@csrf_exempt
def new_transaction_signal(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)

        # OLD Signal
        # request_body = {'portfolio_code': 'TST',
        #                 'account_id': 6,
        #                 'security': 74,
        #                 'transaction_type': 'Close',
        #                 'quantity': 1,
        #                 }
        # NEW Signal
        # request_body = {'portfolio_code': 'TST',
        #                 'security': 74,
        #                 'transaction_type': 'Close',
        #                 'quantity': 1,
        #                 }

        # Close transaction from the Risk view
        if request_body['transaction_type'] == 'risk_closure':
            transactions = pd.DataFrame(Transaction.objects.filter(id__in=request_body['ids']).values())
            for index, transaction in transactions.iterrows():
                execution = TradeExecution(portfolio_code=transaction['portfolio_code'],
                                           account_id=transaction['account_id'],
                                           security=transaction['security'],
                                           )
                closed_transactions = pd.DataFrame(Transaction.objects.filter(transaction_link_code=transaction['id']).values())
                if len(closed_transactions) == 0:
                    closed_out_units = 0
                else:
                    closed_out_units = closed_transactions['quantity'].sum()
                quantity = transaction['quantity'] - abs(closed_out_units)
                execution.close(transaction=transaction, quantity=quantity)
            return JsonResponse('Transactions are closed', safe=False)

        # Checking if trade routing exists
        try:
            routing = TradeRoutes.objects.get(portfolio_code=request_body['portfolio_code'],
                                              inst_id=request_body['security_id'])
        except:
            Notifications(portfolio_code=request_body['portfolio_code'],
                          message='Missing trade routing. Security Code: ' + str(request_body['security_id']),
                          sub_message='Error',
                          broker_name='-').save()
            return JsonResponse({}, safe=False)

        if routing.is_active == 0:
            Notifications(portfolio_code=request_body['portfolio_code'],
                          message='Rejected Trade. Inactive Routing. Security: ' + str(request_body['security_id']),
                          sub_message='Inactive trade routing',
                          broker_name='-').save()
            return JsonResponse({}, safe=False)

        # This code determines if trade routing quantity has to be applied or manual quantity multiplier
        if 'manual' in request_body:
            quantity_multiplier = 1
            account_id = request_body['account_id']
        else:
            quantity_multiplier = routing.quantity
            account_id = routing.broker_account_id

        # Initalizing trade execution
        # Account ID determines the broker and the broker account to trade on
        try:
            execution = TradeExecution(
                portfolio_code=request_body['portfolio_code'],
                account_id=request_body['account_id'],
                security_id=request_body['security_id']
            )
        except ValueError as e:
            return JsonResponse({'response': str(e)})


        if request_body['transaction_type'] == "Close All":
            open_transactions = Transaction.objects.filter(security=request_body['security_id'],
                                                           is_active=1,
                                                           portfolio_code=request_body['portfolio_code'])
            for transaction in open_transactions:
                execution.close(transaction=transaction)

        # Liquidating the whole portfolio and open trades at the same time
        elif request_body['transaction_type'] == 'Liquidate':
            open_transactions = Transaction.objects.filter(is_active=1,
                                                           portfolio_code=request_body['portfolio_code'])
            for transaction in open_transactions:
                execution.close(transaction=transaction)

        # Partial close out of an existing position
        elif request_body['transaction_type'] == 'Close Out':
            transaction = Transaction.objects.get(id=request_body['id'])
            execution.close(transaction=transaction, quantity=request_body['quantity'])

        # Closing a single open trade with the rest outstanding quantity
        elif request_body['transaction_type'] == 'Close':
            transaction = Transaction.objects.get(id=request_body['id'])
            # print('PARENT')
            # print(transaction)
            execution.close(transaction=transaction)

        # This is the trade execution
        else:
            if 'sl' in request_body:
                latest_nav = list(Nav.objects.filter(portfolio_code=request_body['portfolio_code']).order_by('date').values_list('total', flat=True))[-1]
                risked_amount = latest_nav * float(request_body['risk_perc'])
                current_price = execution.get_market_price()
                price_diff = abs(current_price-float(request_body['sl']))
                quantity = str(int(risked_amount / price_diff))
                request_body['quantity'] = quantity
            execution.new_trade(transaction_type=request_body['transaction_type'],
                                quantity=float(request_body['quantity']) * quantity_multiplier)
        # calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=trade_date)
        return JsonResponse({}, safe=False)


# I will have to review the logic of the trade execution class and rework its functions

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_trade_by_id(request):
    try:
        # Parse JSON request body
        request_body = json.loads(request.body.decode('utf-8'))
        transaction_ids = request_body.get("ids", [])

        # Check if transaction_ids is a valid list
        if not isinstance(transaction_ids, list) or not transaction_ids:
            return JsonResponse({"error": "Invalid or missing transaction IDs"}, status=400)

        open_transactions = Transaction.objects.filter(id__in=transaction_ids)
        for transaction in open_transactions:
            execution = TradeExecution(portfolio_code=transaction.portfolio_code,
                                       account_id=transaction.account_id,
                                       security_id=transaction.security_id,
                                       )

            execution.close(transaction=transaction)

        # Return response
        return JsonResponse({
            "message": f"transactions closed successfully",
            "closed_transaction_ids": transaction_ids
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['POST'])
def trade(request):
    # IDE KELLENI FOG EGY TOKEN ALAPÚ HITELESITÉSI FOLYAMAT AMI A BEJÖVŐ JEL ALAPJÁN AZONOSITJA AZ ÜGYFELET

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = ['portfolio_code', 'security_id', 'transaction_type', 'quantity']
    missing = [field for field in required_fields if field not in data]

    tx_type = data.get('transaction_type')
    signal_type = 'OPEN' if tx_type in ['Purchase', 'Sale'] else 'CLOSE'
    data['type'] = signal_type

    source = 'EXTERNAL' if 'account_id' not in data else 'INTERNAL'

    error_message = ''
    status = 'PENDING'

    if missing:
        error_message = f"Missing required fields: {', '.join(missing)}"
        status = 'FAILED'

    portfolio_data = None

    # Portfolio Validation
    try:
        portfolio_data = Portfolio.objects.get(portfolio_code=data.get('portfolio_code'))
    except Portfolio.DoesNotExist:
        error_message = "Portfolio does not exist"
        status = 'FAILED'

    # Trade and Signal Trade Validations
    if status == 'PENDING':
        if not portfolio_data.trading_allowed:
            error_message = "Trading is not allowed for this portfolio."
            status = 'FAILED'
        elif source == 'EXTERNAL' and not portfolio_data.allow_external_signals:
            error_message = "External signals are not allowed for this portfolio."
            status = 'FAILED'

    # Trade Routing Validation
    if status == 'PENDING' and source == 'EXTERNAL':
        try:
            routing = TradeRoutes.objects.get(
                portfolio_code=data.get('portfolio_code'),
                inst_id=data.get('security_id')
            )
            data['account_id'] = routing.broker_account_id
        except TradeRoutes.DoesNotExist:
            error_message = "Missing trade routing for this security."
            status = 'FAILED'

    # Signal Creation
    signal = Signal.objects.create(
        portfolio=portfolio_data,
        type=signal_type,
        raw_data=data,
        status=status,
        error_message=error_message,
        source=source
    )

    if status == 'PENDING':
        execute_trade_signal(signal.id) #.delay(signal.id) ezt kell majd átirni ha celerybol fut majd

    return JsonResponse(
        {'status': status, 'signal_id': signal.id, 'error_message': error_message if status != 'PENDING' else None},
        status=202 if status == 'PENDING' else 400
    )


