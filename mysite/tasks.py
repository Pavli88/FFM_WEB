from celery import shared_task
import time
from calculations.processes.valuation.valuation import calculate_holdings

@shared_task
def long_running_task():
    print("TEST TASK")
    time.sleep(10)  # Simulating a long-running task
    return "Task Complete!"

@shared_task
def val(portfolio_code, calc_date):
    response = calculate_holdings(portfolio_code=portfolio_code, calc_date=calc_date)
    return response

