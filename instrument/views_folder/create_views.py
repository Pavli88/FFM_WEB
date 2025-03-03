import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from instrument.instrument_pricing.oanda_pricing import oanda_pricing
from instrument.models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_instrument(request):
    try:
        request_data = request.data  # Use DRF's request.data instead of manually loading JSON
        user = request.user
        # Validate required fields
        required_fields = ['name', 'country', 'group', 'type', 'currency']
        missing_fields = [field for field in required_fields if field not in request_data]

        if missing_fields:
            return Response({'error': f'Missing fields: {", ".join(missing_fields)}'}, status=400)

        # Create and save instrument
        instrument, created = Instruments.objects.get_or_create(
            user=user,
            name=request_data['name'],
            defaults={
                'country': request_data['country'],
                'group': request_data['group'],
                'type': request_data['type'],
                'currency': request_data['currency'],
            }
        )

        if created:
            return Response({'message': 'Instrument is saved successfully!'}, status=201)
        else:
            return Response({'message': 'Instrument already exists!'}, status=200)

    except ValidationError as e:
        return Response({'error': f'Validation error: {str(e)}'}, status=400)

    except Exception as e:
        return Response({'error': f'Error occurred: {str(e)}'}, status=500)


@csrf_exempt
def new_broker_ticker(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        ticker_assigned = Tickers.objects.filter(inst_code=request_data['inst_code'], source=request_data['source']).exists()
        if ticker_assigned:
            return JsonResponse('Ticker has already been assigned to this security at this broker!', safe=False)
        try:
            Tickers(
                inst_code=request_data['inst_code'],
                source=request_data['source'],
                source_ticker=request_data['source_ticker'],
                margin=request_data['margin']
            ).save()
            response = 'Broker ticker is saved!'
        except:
            response = 'Broker ticker already exists!'

        return JsonResponse(response, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_price(request):
    price_list = request.data.get('data', [request.data])

    updated_records = 0
    created_records = 0

    for price_record in price_list:
        try:
            instrument_id = int(price_record['instrument_id'])
            date = price_record['date']
            price_value = float(price_record['price'])
            source = price_record.get('source', 'unknown')

            price, created = Prices.objects.update_or_create(
                date=date,
                instrument_id=instrument_id,
                defaults={'price': price_value, 'source': source}
            )

            if created:
                created_records += 1
            else:
                updated_records += 1
        except (ValueError, KeyError):
            continue

    return Response({
        'message': 'Prices processed successfully',
        'updated': updated_records,
        'created': created_records
    }, status=200)


@csrf_exempt
def instrument_pricing(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        if request_body['broker'] == 'oanda':
            oanda_pricing(start_date=request_body['start_date'], end_date=request_body['end_date'])

        return JsonResponse('Pricing job has run', safe=False)