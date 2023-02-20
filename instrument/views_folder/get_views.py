from django.http import JsonResponse

# Model import
from instrument.models import Instruments


def get_instruments(request):
    if request.method == "GET":
        print('INSTUMENTS')
        if request.GET.get('name') is None:
            instrument_name = ''
        else:
            instrument_name = request.GET.get('name')
        filters = {}
        for key, value in request.GET.items():
            if key in ['id', 'code', 'group', 'country', 'type', 'currency']:
                filters[key] = value
        instruments = Instruments.objects.filter(name__contains=instrument_name).filter(**filters).values()
        response = list(instruments)
        return JsonResponse(response, safe=False)