from celery import shared_task
from portfolio.models import Portfolio, Transaction, Nav, TradeRoutes
from django.http import JsonResponse
from trade_app.views_folder.create_view import TradeExecution

@shared_task(queue='trade_signal')
def execute_trade_signal(signal):
    print(signal)
    try:
        execution = TradeExecution(
            portfolio_code=signal['portfolio_code'],
            account_id=signal['account_id'],
            security_id=signal['security_id']
        )
    except ValueError as e:
        return JsonResponse({'response': str(e)})

    if signal['transaction_type'] == "Close All":
        open_transactions = Transaction.objects.filter(security=signal['security_id'],
                                                       is_active=1,
                                                       portfolio_code=signal['portfolio_code'])
        for transaction in open_transactions:
            execution.close(transaction=transaction)

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

        execution.new_trade(transaction_type=signal['transaction_type'],
                            quantity=float(signal['quantity']) * quantity_multiplier)
    # calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=trade_date)
