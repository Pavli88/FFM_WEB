from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from portfolio.models import Robots, Portfolio, CashFlow
import json


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