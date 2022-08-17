from django.shortcuts import render, redirect
from instrument.forms import *
from instrument.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def new_instrument(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            Instruments(instrument_name=request_data['inst_name'],
                        inst_code=request_data['internal_code'],
                        source_code=request_data['source_code'],
                        currency=request_data['currency'],
                        source=request_data['broker']).save()
            response = 'Instrument is Saved!'
        except:
            response = 'Instrument Internal Code Exists in Database!'
        return JsonResponse(response, safe=False)


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


def get_instruments(request):
    if request.method == "GET":
        if request.GET.get('instrument_name') is None:
            instrument_name = ''
        else:
            instrument_name = request.GET.get('instrument_name')
        filters = {}
        for key, value in request.GET.items():
            if key in ['id', 'instrument_type', 'source', 'inst_code', 'currency']:
                filters[key] = value
        instruments = Instruments.objects.filter(instrument_name__contains=instrument_name).filter(**filters).values()
        response = list(instruments)
        return JsonResponse(response, safe=False)

