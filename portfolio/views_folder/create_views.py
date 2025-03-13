from django.http import JsonResponse
from portfolio.models import TradeRoutes, PortGroup, Portfolio, Nav, Transaction
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from calculations.processes.valuation.valuation import calculate_holdings
from datetime import datetime

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
# @permission_classes([IsAuthenticated])
def create_portfolio(request):
    try:
        body_data = json.loads(request.body.decode('utf-8'))
        print(body_data)
        user = request.user

        required_fields = ["port_name", "port_code", "port_type", "port_currency", "inception_date"]

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
        if Portfolio.objects.filter(user=user, portfolio_code=body_data["port_code"]).exists():
            return JsonResponse({'msg': "Portfolio code already exists for this user!", 'port': 0}, status=400)

        if Portfolio.objects.filter(user=user, portfolio_name=body_data["port_name"]).exists():
            return JsonResponse({'msg': "Portfolio name already exists for this user!", 'port': 0}, status=400)

        # Create Portfolio
        port = Portfolio(
            portfolio_name=body_data["port_name"],
            portfolio_code=body_data["port_code"],
            portfolio_type=body_data["port_type"],
            currency=body_data["port_currency"],
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
def transaction(request):
    try:
        # Parse the request body
        body_data = json.loads(request.body.decode('utf-8'))

        # Extract transaction_type
        transaction_type = body_data.get("transaction_type")

        # Define transaction categories
        CASH_TRANSACTIONS = {"Subscription", "Redemption", "Commission"}
        INSTRUMENT_TRANSACTIONS = {"Purchase", "Sale"}

        # Determine transaction category
        if transaction_type in CASH_TRANSACTIONS:
            category = "Cash Transaction"
            transaction = Transaction(
                portfolio_code=body_data["portfolio_code"],
                portfolio_id=body_data['portfolio_id'],
                security_id=body_data['security'],
                quantity=body_data['quantity'],
                trade_date=body_data['trade_date'],
                transaction_type=transaction_type,
            ).new_cash_transaction()
            print(transaction)
        elif transaction_type in INSTRUMENT_TRANSACTIONS:
            category = "Parent Instrument Transaction"
            transaction = Transaction(
                portfolio_code=body_data["portfolio_code"],
                portfolio_id=body_data['portfolio_id'],
                security_id=body_data['security'],
                quantity=body_data['quantity'],
                trade_date=body_data['trade_date'],
                transaction_type=transaction_type,
            ).new_parent_transaction(price=body_data['price'])
        elif transaction_type is None:
            category = "Child Instrument Transaction"
            transaction = Transaction(
                portfolio_code=body_data["portfolio_code"],
                portfolio_id=body_data['portfolio_id'],
                security_id=body_data['security'],
                quantity=body_data['quantity'],
                trade_date=body_data['trade_date'],
            ).new_child_transaction(parent_id=body_data['parent_id'])
            transaction_type='Child Transaction'
        else:
            return JsonResponse({"msg": "Invalid transaction type"}, status=400)

        # Simulate saving transaction (you can integrate database logic here)
        response_data = {
            "msg": transaction,
            "category": category,
            "transaction_type": transaction_type
        }

        return JsonResponse(response_data, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"msg": "Invalid JSON format"}, status=400)

    except Exception as e:
        return JsonResponse({"msg": f"An error occurred: {str(e)}"}, status=500)

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
