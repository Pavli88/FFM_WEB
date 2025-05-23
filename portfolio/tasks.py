from celery import shared_task

@shared_task(queue='valation', bind=True, max_retries=3)
def run_valuation(self):
    print('RUN VALUATION')