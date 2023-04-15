from django.shortcuts import render, redirect
from instrument.forms import *
from instrument.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def update_instrument(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        updates = {}
        for key, value in request_data.items():
            if key in ['instrument_name', 'instrument_type', 'source', 'inst_code', 'currency', 'source_code']:
                updates[key] = value
        try:
            Instruments.objects.filter(id=request_data['id']).update(**updates)
            response = 'Instrument Updated!'
        except:
            response = 'Instrument Internal Code Exists in Database!'
        return JsonResponse(response, safe=False)


@csrf_exempt
def delete_instrument(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        # I will have to add here a validation section which checks if the security is included in transactions
        try:
            Instruments.objects.get(id=request_data['id']).delete()
            response = 'Instrument is deleted!'
        except:
            response = 'Please select an instrument!'
        # print(Instruments.objects.get(id=request_data['id']))

        return JsonResponse(response, safe=False)




