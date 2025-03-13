import pandas as pd
from django.http import JsonResponse
from django.db.models import Q
from instrument.models import Instruments, Tickers, Prices
from app_functions.request_functions import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_instruments(request):
    try:
        instrument_name = request.GET.get('name', '')  # Default to empty string if not provided
        countries = request.GET.getlist('country')  # Get multiple values from query params
        group = request.GET.getlist('group')
        types = request.GET.getlist('type')
        currencies = request.GET.getlist('currency')

        # Construct filters dynamically using Q objects
        filters = Q(user=request.user) | Q(user__isnull=True)  # Allow instruments with NULL user or assigned user

        if instrument_name:
            filters &= Q(name__icontains=instrument_name)  # Case-insensitive search

        if countries:
            filters &= Q(country__in=countries)

        if group:
            filters &= Q(group__in=group)

        if types:
            filters &= Q(type__in=types)

        if currencies:
            filters &= Q(currency__in=currencies)

        # Query the database
        results = Instruments.objects.select_related('user').filter(filters).values()

        return JsonResponse(list(results), safe=False, status=200)

    except Instruments.DoesNotExist:
        return JsonResponse({'error': 'No instruments found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


def get_broker_tickers(request):
    if request.method == "GET":
        return JsonResponse(dynamic_mode_get(request_object=request.GET.items(),
                                             column_list=['inst_code', 'source'],
                                             table=Tickers), safe=False)


def get_prices(request):
    if request.method == "GET":
        prices = dynamic_mode_get(request_object=request.GET.items(),
                                  column_list=['instrument_id', 'date', 'date__gte', 'date__lte'],
                                  table=Prices)
        # print(len(prices))
        if len(prices) == 0:
            return JsonResponse(list({}), safe=False)
        else:
            # print(pd.DataFrame(prices).sort_values('date').to_dict('records'))
            return JsonResponse(pd.DataFrame(prices).sort_values('date').to_dict('records'), safe=False)
