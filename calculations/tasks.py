from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from calculations.processes.valuation.valuation import calculate_holdings

# @shared_task(queue='calculations', bind=True, max_retries=3)
# def execute_valuation(self):
#     channel_layer = get_channel_layer()
#     user_id = request.user.id
#
#     calculate_holdings(portfolio_code=portfolio_code, calc_date=request_body['start_date'])
#
#     async_to_sync(channel_layer.group_send)(
#         f"user_{user_id}",
#         {
#             "type": "process.completed",  # ezt fogja a consumer feldolgozni
#             "payload": {
#                 "message": "Valuation process completed successfully.",
#                 "status": True
#             }
#         }
#     )