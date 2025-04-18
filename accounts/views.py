from accounts.models import *
from accounts.account_functions import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .serializers import BrokerAccountSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_account(request):
    request_data = json.loads(request.body.decode('utf-8'))
    account, created = BrokerAccounts.objects.get_or_create(
        broker_name=request_data['broker_name'],
        account_number=request_data['account_number'],
        user=request.user,
        defaults={
            'account_name': request_data['account_name'],
            'env': request_data['env'],
            'access_token': request_data['token'],
            'currency': request_data['currency'],
        }
    )

    # Check if account was created or already exists
    if created:
        return JsonResponse({"message": "Account is created successfully!"}, status=201)
    else:
        return JsonResponse({"message": "Account already exists in the database!"}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_account(request, pk):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    try:
        account = BrokerAccounts.objects.get(pk=pk)
    except BrokerAccounts.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)

    serializer = BrokerAccountSerializer(account, data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)
    else:
        return JsonResponse(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accounts(request):
    filters = {key: value for key, value in request.GET.items() if value}
    filters['user'] = request.user
    try:
        accounts = BrokerAccounts.objects.select_related('user').filter(**filters)

        if not accounts.exists():
            return JsonResponse({"error": "No accounts found for the given broker"}, status=404)

        return JsonResponse(list(accounts.values()), safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_brokers(request):
    brokers = Brokers.objects.filter(
        Q(user=request.user) | Q(api_support=True)
    ).values()
    return JsonResponse(list(brokers), safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_broker(request):
    broker = request.data.get('broker', '').strip()
    type = request.data.get('type')
    broker_code = request.data.get('broker_code', '').strip()

    # Validate required fields
    if not broker or not broker_code:
        return Response({"error": "Both broker and broker_code are required."}, status=400)

    # Check if broker_code already exists
    broker_instance, created = Brokers.objects.get_or_create(
        broker_code=broker_code,
        api_support=True,
        defaults={
            'broker': broker,
            'type': type,
            'user': request.user,
        }
    )

    if not created:
        return Response({"error": "Broker code already exists!"}, status=400)

    return Response({"message": "New broker saved to database!"}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    request_data = json.loads(request.body.decode('utf-8'))
    BrokerAccounts.objects.get(id=request_data['id']).delete()
    return JsonResponse({'message': 'Account is deleted'}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_broker(request):
    request_data = json.loads(request.body.decode('utf-8'))
    Brokers.objects.get(id=request_data['id']).delete()
    return JsonResponse({'message': 'Broker is deleted'}, status=200)
