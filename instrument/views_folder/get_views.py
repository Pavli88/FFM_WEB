from django.http import JsonResponse

# Model import
from instrument.models import Instruments, Tickers


def get_instruments(request):
    if request.method == "GET":
        column_names = [field.name for field in Instruments._meta.fields]
        if request.GET.get('name') is None:
            instrument_name = ''
        else:
            instrument_name = request.GET.get('name')
        filters = {}
        for key, value in request.GET.items():
            if key in column_names:
                filters[key] = value
        instruments = Instruments.objects.filter(name__contains=instrument_name).filter(**filters).values()
        response = list(instruments)
        return JsonResponse(response, safe=False)


def get_broker_tickers(request):
    print("BROKER TICKERS")
    if request.method == "GET":
        return JsonResponse(list(Tickers.objects.filter(inst_code=request.GET.get('id')).values()), safe=False)