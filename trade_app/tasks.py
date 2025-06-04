from celery import shared_task
from portfolio.models import Portfolio, Transaction, Nav, TradeRoutes
from django.http import JsonResponse
from django.utils import timezone
from trade_app.views_folder.create_view import TradeExecution
from trade_app.models import Signal, Order
from django.db import transaction as db_transaction
from calculations.processes.valuation.valuation import calculate_holdings
from datetime import date

# @shared_task(queue='trade_signal', bind=True, max_retries=3) -> itt meg tudom mondani hányszor próbálja újra
# self et bele kell rakni az argumentumok közé ha celery task lesz
@shared_task(queue='trade_signal', bind=True, max_retries=3)
def execute_trade_signal(self, signal_id):
    try:
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
                signal=signal_instance,
                broker_account_id=signal['account_id'],
                portfolio=signal_instance.portfolio,
                security_id=signal['security_id'],
                symbol='N/A',
                side='BUY' if signal['transaction_type'] == 'Purchase' else 'SELL',
                quantity=signal.get('quantity', 0),
                status='FAILED',
                error_message=str(e)
            )
            signal_status = 'FAILED'
            error_message = '-'
            signal_instance.status = signal_status
            signal_instance.error_message = error_message
            signal_instance.executed_at = timezone.now()
            signal_instance.save()
            return

        if signal['transaction_type'] == "Close All":
            status_list = []

            with db_transaction.atomic():
                open_transactions = Transaction.objects.select_for_update().filter(
                    security=signal['security_id'],
                    is_active=1,
                    portfolio_code=signal['portfolio_code']
                )

                if not open_transactions:
                    signal_status = 'REJECTED'
                    error_message = 'There are no open trades to close on the platform.'
                else:
                    for transaction in open_transactions:
                        response = execution.close(transaction=transaction)
                        status_list.append(response['status'])
                        Order.objects.create(
                            signal=signal_instance,
                            broker_account_id=signal['account_id'],
                            portfolio=signal_instance.portfolio,
                            security_id=signal['security_id'],
                            symbol=response['data'].get('symbol', 'N/A'),
                            side='SELL' if transaction.transaction_type == 'Purchase' else 'BUY',
                            quantity=signal.get('quantity', 0),
                            status=response['status'],
                            executed_price=response['data'].get('executed_price'),
                            fx_rate=response['data'].get('fx_rate'),
                            broker_order_id=response['data'].get('broker_order_id'),
                            error_message=None if response['status'] == 'EXECUTED' else response.get('message', '')
                        )

                    if all(status == 'FAILED' for status in status_list):
                        signal_status = 'FAILED'
                        error_message = 'All trade closures failed at broker.'
                    elif all(status == 'EXECUTED' for status in status_list):
                        signal_status = 'EXECUTED'
                        error_message = '-'
                    else:
                        signal_status = 'PARTIALLY EXECUTED'
                        error_message = 'Some trades executed, some failed.'

        elif signal['transaction_type'] == 'Liquidate':
            open_transactions = Transaction.objects.filter(
                is_active=1,
                portfolio_code=signal['portfolio_code']
            )

            if not open_transactions:
                signal_status = 'REJECTED'
                error_message = 'There are no open trades to liquidate on the platform.'
            else:
                signal_status = 'EXECUTED'
                error_message = '-'

            for transaction in open_transactions:
                execution.close(transaction=transaction)

        elif signal['transaction_type'] == 'Close Out':
            transaction = Transaction.objects.get(id=signal['id'])
            execution.close(transaction=transaction, quantity=signal['quantity'])

        elif signal['transaction_type'] == 'Close':
            transaction = Transaction.objects.get(id=signal['id'])

            if not transaction:
                signal_status = 'REJECTED'
                error_message = 'There are no open trades to liquidate on the platform.'
            else:
                response  = execution.close(transaction=transaction)
                signal_status = response['status']
                error_message = response['message']

                Order.objects.create(
                    signal=signal_instance,
                    broker_account_id=signal['account_id'],
                    portfolio=signal_instance.portfolio,
                    security_id=signal['security_id'],
                    symbol=response['data'].get('symbol', 'N/A'),
                    side='SELL' if transaction.transaction_type == 'Purchase' else 'BUY',
                    quantity=signal.get('quantity', 0),
                    status=response['status'],
                    executed_price=response['data'].get('executed_price'),
                    fx_rate=response['data'].get('fx_rate'),
                    broker_order_id=response['data'].get('broker_order_id'),
                    error_message=None if response['status'] == 'EXECUTED' else response.get('message', '')
                )

        else:
            response = execution.new_trade(
                transaction_type=signal['transaction_type'],
                quantity=float(signal['quantity'])
            )

            Order.objects.create(
                signal=signal_instance,
                broker_account_id=signal['account_id'],
                portfolio=signal_instance.portfolio,
                security_id=signal['security_id'],
                symbol=response['data'].get('symbol', 'N/A'),
                side='BUY' if signal['transaction_type'] == 'Purchase' else 'SELL',
                quantity=signal.get('quantity', 0),
                status=response['status'],
                executed_price=response['data'].get('executed_price'),
                fx_rate=response['data'].get('fx_rate'),
                broker_order_id=response['data'].get('broker_order_id'),
                error_message=None if response['status'] == 'EXECUTED' else response.get('message', '')
            )

            signal_status = 'EXECUTED'
            error_message = '-'

        signal_instance.status = signal_status
        signal_instance.error_message = error_message
        signal_instance.executed_at = timezone.now()
        signal_instance.save()

    except Exception as e:
        signal_instance.status = 'FAILED'
        signal_instance.error_message = str(e)
        signal_instance.save()
        raise self.retry(exc=e, countdown=10) #-> ez automatikusan ujra probálja a celery ben ha technikai hiba történik
