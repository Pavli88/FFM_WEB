from celery import shared_task
from portfolio.models import Portfolio, Transaction, Nav, TradeRoutes
from django.http import JsonResponse
from django.utils import timezone
from trade_app.views_folder.create_view import TradeExecution
from trade_app.models import Signal, Order

# @shared_task(queue='trade_signal')
def execute_trade_signal(signal_id):

    signal_instance = Signal.objects.get(id=signal_id)
    signal = signal_instance.raw_data

    try:
        execution = TradeExecution(
            portfolio_code=signal['portfolio_code'],
            account_id=signal['account_id'],
            security_id=signal['security_id']
        )
    except ValueError as e:

        Order.objects.create(
            signal=signal,
            broker_account_id=signal['account_id'],
            portfolio=signal_instance.portfolio,
            security_id=signal['security_id'],
            symbol='N/A',
            side='BUY' if signal['transaction_type'] == 'Purchase' else 'SELL',
            quantity=signal.get('quantity', 0),
            status='FAILED',
            error_message=str(e)
        )
        signal_instance.status = 'EXECUTED'
        signal_instance.save()
        return

    if signal['transaction_type'] == "Close All":
        open_transactions = Transaction.objects.filter(security=signal['security_id'],
                                                       is_active=1,
                                                       portfolio_code=signal['portfolio_code'])
        for transaction in open_transactions:
            response = execution.close(transaction=transaction)

            Order.objects.create(
                signal=signal_instance,
                broker_account_id=signal['account_id'],
                portfolio=signal_instance.portfolio,
                security_id=signal['security_id'],
                symbol=response['data']['symbol'],
                side='SELL' if transaction.transaction_type == 'Purchase' else 'BUY',
                quantity=signal.get('quantity', 0),
                status=response['status'],
                executed_price=response['data']['executed_price'],
                fx_rate=response['data']['fx_rate'],
                broker_order_id=response['data']['broker_order_id'],
            )

    # Liquidating the whole portfolio and open trades at the same time
    elif signal['transaction_type'] == 'Liquidate':
        open_transactions = Transaction.objects.filter(is_active=1,
                                                       portfolio_code=signal['portfolio_code'])
        for transaction in open_transactions:
            execution.close(transaction=transaction)

    # Partial close out of an existing position
    elif signal['transaction_type'] == 'Close Out':
        transaction = Transaction.objects.get(id=signal['id'])
        execution.close(transaction=transaction, quantity=signal['quantity'])

    # Closing a single open trade with the rest outstanding quantity
    elif signal['transaction_type'] == 'Close':
        transaction = Transaction.objects.get(id=signal['id'])
        execution.close(transaction=transaction)

    # This is the trade execution
    else:
        if 'sl' in signal:
            latest_nav = list(
                Nav.objects.filter(portfolio_code=signal['portfolio_code']).order_by('date').values_list('total',
                                                                                                               flat=True))[
                -1]
            risked_amount = latest_nav * float(signal['risk_perc'])
            current_price = execution.get_market_price()
            price_diff = abs(current_price - float(signal['sl']))
            quantity = str(int(risked_amount / price_diff))
            signal['quantity'] = quantity

        response = execution.new_trade(
            transaction_type=signal['transaction_type'],
            quantity=float(signal['quantity']))

        Order.objects.create(
            signal=signal_instance,
            broker_account_id=signal['account_id'],
            portfolio=signal_instance.portfolio,
            security_id=signal['security_id'],
            symbol=response['data']['symbol'],
            side='BUY' if signal['transaction_type'] == 'Purchase' else 'SELL',
            quantity=signal.get('quantity', 0),
            status=response['status'],
            executed_price=response['data']['executed_price'],
            fx_rate=response['data']['fx_rate'],
            broker_order_id=response['data']['broker_order_id'],
        )

    signal_instance.status = 'EXECUTED'
    signal_instance.executed_at = timezone.now()

    # except Exception as e:
    # signal.status = 'FAILED'
    # signal.error_message = str(e)
    # raise self.retry(exc=e, countdown=10)
    #
    #
    signal_instance.save()
    # calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=trade_date)
