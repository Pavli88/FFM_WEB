import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from instrument.models import *


@csrf_exempt
def new_instrument(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        print(request_data)
        try:
            Instruments(name=request_data['name'],
                        code=request_data['code'],
                        country=request_data['country'],
                        group=request_data['group'],
                        currency=request_data['currency'],
                        type=request_data['type']).save()
            response = 'Instrument is Saved!'
        except:
            response = 'Instrument Internal Code Exists in Database!'
        return JsonResponse(response, safe=False)