from django.http import JsonResponse
from portfolio.models import TradeRoutes, PortGroup, Portfolio, Nav, Transaction
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trade_routing(request):
    request_data = json.loads(request.body.decode('utf-8'))
    if TradeRoutes.objects.filter(portfolio_code=request_data['portfolio_code'],
                                  inst_id=request_data['inst_id']).exists():
        return JsonResponse({'response': 'Security is already mapped to this portfolio'}, safe=False)
    else:
        TradeRoutes(portfolio_code=request_data['portfolio_code'],
                    inst_id=request_data['inst_id'],
                    ticker_id=request_data['ticker_id'],
                    broker_account_id=request_data['broker_account_id']).save()
        return JsonResponse({'response': 'Security mapping is completed'}, safe=False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_portfolio(request):
    try:
        body_data = json.loads(request.body.decode('utf-8'))
        user = request.user

        if Portfolio.objects.filter(user=user, portfolio_code=body_data["port_code"]).exists():
            return JsonResponse({'msg': "Portfolio code already exists for this user!", 'port': 0}, status=400)

        if Portfolio.objects.filter(user=user, portfolio_name=body_data["port_name"]).exists():
            return JsonResponse({'msg': "Portfolio name already exists for this user!", 'port': 0}, status=400)

        port = Portfolio(
            portfolio_name=body_data["port_name"],
            portfolio_code=body_data["port_code"],
            portfolio_type=body_data["port_type"],
            currency=body_data["port_currency"],
            inception_date=body_data["inception_date"],
            user=user
        )
        port.save()
        print(port.id)
        Nav.objects.create(date=body_data["inception_date"], portfolio=port)

        return JsonResponse({'msg': "New Portfolio is created!", 'port': port.id}, status=201)
    except KeyError as e:
        return JsonResponse({'msg': f"Missing field: {str(e)}"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'msg': "Invalid JSON format"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_transaction(request):
    request_body = json.loads(request.body.decode('utf-8'))

    print('NEW TRANSACTION')
    print(request_body)

    if 'initial_cash' in request_body:
        portfolio = Portfolio.objects.get(portfolio_code=request_body['portfolio_code'])
        portfolio.status = 'Funded'
        portfolio.save()
        del request_body['initial_cash']

    request_body['quantity'] = float(request_body['quantity']) if request_body['quantity'] else 0.0
    Transaction.objects.create(**request_body)
    # calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=request_body['trade_date'])
    return JsonResponse({"message": "Transaction is created!", 'success': True}, safe=False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_portgroup(request):
    request_body = json.loads(request.body.decode('utf-8'))

    parent_id = request_body.get('parent_id')
    portfolio_id = request_body.get('portfolio_id')

    if PortGroup.objects.filter(parent_id=parent_id, portfolio_id=portfolio_id).exists():
        return JsonResponse({"message": "Portfolio is already assigned to a portfolio group"}, status=409)

    PortGroup.objects.create(parent_id=parent_id, portfolio_id=portfolio_id)

    return JsonResponse({"message": "Portfolio is added to the group", "success": True}, status=201)
