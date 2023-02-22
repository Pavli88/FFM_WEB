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
        column_names = [field.name for field in Instruments._meta.fields]
        print(column_names)
        try:
            Instruments(name=request_data['name'],
                        code=request_data['code'],
                        ticker=request_data['ticker'],
                        country=request_data['country'],
                        group=request_data['group'],
                        type=request_data['type'],
                        currency=request_data['currency'],
                        ).save()
            response = 'Instrument is Saved!'
        except:
            response = 'Instrument code already exists!'

        # except:
        #     response = 'Instrument Internal Code Exists in Database!'
        return JsonResponse(response, safe=False)