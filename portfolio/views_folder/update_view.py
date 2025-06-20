from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction, TradeRoutes, Holding
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_portfolio(request):
    request_data = request.data
    print('UPDATE')
    portfolio_id = request_data.get('id')
    if not portfolio_id:
        return JsonResponse({'response': 'Portfolio ID is required'}, status=400)

    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
    except ObjectDoesNotExist:
        return JsonResponse({'response': 'Portfolio not found'}, status=404)

    # Get all valid model fields
    valid_fields = {field.name for field in Portfolio._meta.get_fields()}

    # Update only valid fields
    updated = False
    for key, value in request_data.items():
        if key in valid_fields and key != 'id':  # Prevent updating the ID
            setattr(portfolio, key, value)
            updated = True

    if updated:
        portfolio.save()
        return JsonResponse({'response': 'Portfolio updated successfully'}, status=200)
    else:
        return JsonResponse({'response': 'No valid fields to update'}, status=400)


@csrf_exempt
def update_transaction(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))

        try:
            transaction = Transaction.objects.get(id=request_data['id'])
            for key, value in request_data.items():
                setattr(transaction, key, value)
            transaction.save()
            return JsonResponse({'response': 'Transaction is updated'}, safe=False)
        except:
            return JsonResponse({'response': 'Error during update'}, safe=False)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_trade_routing(request):
    request_body = json.loads(request.body.decode('utf-8'))
    try:
        trade_route = TradeRoutes.objects.get(id=request_body['id'])
        trade_route.is_active = request_body['is_active']
        trade_route.quantity = request_body['quantity']
        trade_route.broker_account_id = request_body['broker_account_id']
        trade_route.save()
        return JsonResponse({'message': 'Trade routing is updated'}, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Failed to update trade routing'}, safe=False)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_label(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        row_id = request_body.get('row_id')
        label_color = request_body.get('label_color')  # lehet hex string vagy None

        if not row_id:
            return JsonResponse({'error': 'Missing row_id'}, status=400)

        holding = Holding.objects.filter(id=row_id).first()
        if not holding:
            return JsonResponse({'error': 'Holding not found'}, status=404)

        holding.label_color = label_color  # lehet None is!
        holding.save()

        return JsonResponse({'message': 'Label updated', 'row_id': row_id, 'label_color': label_color})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)