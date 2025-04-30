from accounts.account_functions import *
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .serializers import BrokerAccountSerializer
from django.forms.models import model_to_dict
from broker_apis.capital import CapitalBrokerConnection

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


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def broker_credentials(request):
    if request.method == 'GET':
        filters = {key: value for key, value in request.GET.items() if value}
        filters['user'] = request.user

        try:
            accounts = BrokerCredentials.objects.select_related('user', 'broker').filter(**filters)
            account_list = []
            for account in accounts:
                account_data = {
                    "id": account.id,
                    "api_token": account.api_token,
                    "environment": account.environment,
                    "email": account.email,
                    "password": account.password,
                    "broker_id": account.broker.id,
                    "broker_name": account.broker.broker,
                    "user": account.user.id,
                }
                account_list.append(account_data)

            if not accounts.exists():
                return JsonResponse({"error": "No broker crendentials were found for the given broker"}, status=404)

            return JsonResponse(account_list, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    elif request.method == 'POST':
        data = request.data

        try:
            broker_id = data.get("broker")
            api_token = data.get("api_token")
            email = data.get("email")
            password = data.get("password")
            environment = data.get("environment")

            if not broker_id:
                return JsonResponse({"error": "Broker is required"}, status=400)

            broker = Brokers.objects.get(pk=broker_id)

            credentials = BrokerCredentials.objects.create(
                user=request.user,
                broker=broker,
                api_token=api_token,
                email=email,
                password=password,
                environment=environment
            )

            return JsonResponse(model_to_dict(credentials), status=201)

        except Brokers.DoesNotExist:
            return JsonResponse({"error": "Broker not found"}, status=404)
        except ValidationError as ve:
            return JsonResponse({"error": str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    elif request.method == 'DELETE':
        try:
            credential_id = request.data.get('id')

            if not credential_id:
                return JsonResponse({"error": "Missing 'id' in request body."}, status=400)

            credential = BrokerCredentials.objects.get(id=credential_id, user=request.user)
            credential.delete()

            return JsonResponse({"message": "Broker credentials deleted successfully."}, status=200)

        except BrokerCredentials.DoesNotExist:
            return JsonResponse({"error": "Broker credentials not found."}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return None


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync(request):
    data = request.data
    print(data)

    if data.get('broker_name') == 'Capital.com':
        print('CAPITAL')

        # Connect to broker API
        con = CapitalBrokerConnection(
            ENV=data['environment'],
            email=data['email'],
            api_password=data['password'],
            api_key=data['api_token']
        )

        # Fetch accounts from broker
        accounts = con.get_accounts()

        created_accounts = []

        for account in accounts:
            print(account)

            account_number = account.get('accountId')
            print(account_number)
            if not account_number:
                continue  # Skip if no account number

            # Check if account already exists for this user and broker
            existing = BrokerAccounts.objects.filter(
                account_number=account_number,
                user=request.user,
                broker_name=data['broker_name']
            ).first()

            if existing:
                print(f"Account {account_number} already exists, skipping.")
                continue  # Skip if already exists

            # Create new BrokerAccounts record
            new_account = BrokerAccounts.objects.create(
                broker_name=data['broker_name'],
                broker_id=data['broker_id'],
                account_name=account.get('accountName', ''),
                account_number=account.get('accountId'),
                account_type=account.get('accountType', ''),
                env=data['environment'],
                currency=account.get('currency', ''),
                user=request.user,
            )

            created_accounts.append(new_account.id)

    return JsonResponse({
        "message": "Sync complete",
        "created_accounts": created_accounts
    }, safe=False)

