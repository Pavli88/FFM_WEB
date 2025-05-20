from django.http import JsonResponse
from portfolio.models import TradeRoutes, PortGroup, Portfolio, Nav, Transaction
from instrument.models import Tickers
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from calculations.processes.valuation.valuation import calculate_holdings
from datetime import datetime
from portfolio.portfolio_functions import create_transaction

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trade_routing(request):
    request_data = json.loads(request.body.decode('utf-8'))

    if TradeRoutes.objects.filter(portfolio_code=request_data['portfolio_code'],
                                  inst_id=request_data['inst_id']).exists():
        return JsonResponse({
            'msg': f"Routing exists for {request_data['inst_id']} at {request_data['portfolio_code']}"},
            status=400)

    try:
        ticker = Tickers.objects.get(
            inst_code=request_data['inst_id'],
            source=request_data['source']
        )
    except Tickers.DoesNotExist:
        return JsonResponse({
            'msg': f"No ticker found for instrument {request_data['inst_id']} with source {request_data['source']}."
        }, status=404)

    TradeRoutes(portfolio_code=request_data['portfolio_code'],
                inst_id=request_data['inst_id'],
                ticker_id=ticker.id,
                broker_account_id=request_data['broker_account_id']).save()
    return JsonResponse({'msg': "New trade routing is created!"}, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_portfolio(request):
    try:
        body_data = json.loads(request.body.decode('utf-8'))
        print(body_data)
        user = request.user

        required_fields = ["port_name", "port_type", "currency", "inception_date"]

        # Check if all required fields are provided
        missing_fields = [field for field in required_fields if field not in body_data]
        if missing_fields:
            return JsonResponse({'msg': f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        # Validate non-empty values
        for field in required_fields:
            if not body_data[field]:
                return JsonResponse({'msg': f"Field '{field}' cannot be empty"}, status=400)

        # Validate inception_date format (assuming YYYY-MM-DD format)
        try:
            inception_date = datetime.strptime(body_data["inception_date"], "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'msg': "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Check for duplicate portfolio code or name for the user
        if Portfolio.objects.filter(user=user, portfolio_name=body_data["port_name"]).exists():
            return JsonResponse({'msg': "Portfolio name already exists for this user!", 'port': 0}, status=400)

        # Create Portfolio
        port = Portfolio(
            portfolio_name=body_data["port_name"],
            portfolio_type=body_data["port_type"],
            currency=body_data["currency"],
            inception_date=inception_date,
            user=user
        )
        port.save()

        # Create Nav entry
        Nav.objects.create(date=inception_date, portfolio=port)

        return JsonResponse({'msg': "New Portfolio is created!", 'port': port.id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'msg': "Invalid JSON format"}, status=400)

    except Exception as e:
        return JsonResponse({'msg': f"An error occurred: {str(e)}"}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_transaction(request):
    request_body = json.loads(request.body.decode('utf-8'))
    if 'initial_cash' in request_body:
        portfolio = Portfolio.objects.get(portfolio_code=request_body['portfolio_code'])
        portfolio.status = 'Funded'
        portfolio.save()
        del request_body['initial_cash']

    request_body['quantity'] = float(request_body['quantity']) if request_body['quantity'] else 0.0
    Transaction.objects.create(**request_body)
    calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=request_body['trade_date'])
    return JsonResponse({"message": "Transaction is created!", 'success': True}, safe=False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transaction(request):
    try:
        transaction_data = json.loads(request.body.decode('utf-8'))
        result = create_transaction(transaction_data)
        status_code = 201 if result.get("status") == "success" else 400
        return JsonResponse(result, status=status_code)
    except json.JSONDecodeError:
        return JsonResponse({"msg": "Invalid JSON format"}, status=400)

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
