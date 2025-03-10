from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Transaction, TradeRoutes, PortGroup, Portfolio
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError

@csrf_exempt
def delete_transaction(request):
    if request.method == "POST":

        request_data = json.loads(request.body.decode('utf-8'))
        print("IDS",request_data['ids'])
        transaction = Transaction.objects.filter(id__in=request_data['ids'])
        # transaction_df = pd.DataFrame(transaction.values())
        # date = transaction_df['trade_date'].min()
        # portfolio_code = transaction_df['portfolio_code'][0]
        # print(date, portfolio_code)
        transaction.delete()
        # calculate_holdings(portfolio_code=portfolio_code, calc_date=date)
        return JsonResponse({'message': 'Transaction is deleted!', 'success': True}, safe=False)


@csrf_exempt
def delete_trade_routing(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        TradeRoutes.objects.get(id=request_data['id']).delete()
        return JsonResponse({'response': 'Trade Routing is deleted!'}, safe=False)


@csrf_exempt
def delete_port_group(request):
    if request.method == "POST":
        print('DELETE NODE')
        request_data = json.loads(request.body.decode('utf-8'))
        PortGroup.objects.get(id=request_data['id']).delete()
        return JsonResponse({'message': 'Portfolio relationship is deleted!', 'success': True}, safe=False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_portfolios(request):
    try:
        portfolio_ids = request.data.get("ids", [])

        if not portfolio_ids or not isinstance(portfolio_ids, list):
            return Response({"message": "Invalid request data", "success": False}, status=400)

        deleted_count, _ = Portfolio.objects.filter(id__in=portfolio_ids).delete()

        if deleted_count == 0:
            return Response({"message": "No portfolios found to delete", "success": False}, status=404)

        return Response({"message": f"{deleted_count} portfolio(s) deleted successfully!", "success": True})

    except ValidationError:
        return Response({"message": "Invalid ID format", "success": False}, status=400)
    except Exception as e:
        return Response({"message": f"An error occurred: {str(e)}", "success": False}, status=500)