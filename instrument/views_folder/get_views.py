import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from instrument.models import Instruments, Tickers, Prices
from app_functions.request_functions import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instruments(request):
    instrument_name = request.GET.get('name', '')  # Default to empty string if not provided
    countries = request.GET.getlist('country')  # Get multiple values from query params
    group = request.GET.getlist('group')
    types = request.GET.getlist('type')
    currencies = request.GET.getlist('currency')

    # Construct filters dynamically
    filters = {}
    print(countries)
    if instrument_name:
        filters['name__icontains'] = instrument_name  # Case-insensitive search

    if countries:
        filters['country__in'] = countries

    if group:
        filters['group__in'] = group

    if types:
        filters['type__in'] = types

    if currencies:
        filters['currency__in'] = currencies

    filters['user'] = request.user
    print("Filters:", filters)  # Debugging

    # Query the database (replace with actual query)
    results = Instruments.objects.select_related('user').filter(**filters).values()

    return JsonResponse(list(results), safe=False)


def get_instrument(request):
    if request.method == "GET":
        return JsonResponse(list(Instruments.objects.filter(id=request.GET.get('id')).values()), safe=False)


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
