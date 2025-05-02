from celery import shared_task
from instrument.instrument_pricing.pricing import (oanda_pricing)
from datetime import datetime, timedelta

@shared_task(queue='prices_queue')
def download_prices():
    today = datetime.today().date()
    oanda_pricing(start_date=today, end_date=today)