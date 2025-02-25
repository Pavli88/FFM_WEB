import json
from mysite.my_functions.general_functions import *
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# Django imports
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from .serializers import ChangePasswordSerializer

# Database imports
from mysite.models import *
from portfolio.models import Portfolio

from mysite.tasks import long_running_task
from mysite.celery import app

# TASK TEST
def start_task(request):
    # Start the Celery task asynchronously
    print("KICKING OF TASK")
    task = long_running_task.delay()

    return JsonResponse({"task_id": task.id, "status": "Task started"})

def check_celery_status(request):
    inspector = app.control.inspect()
    active_workers = inspector.ping()  # Ping all workers

    if active_workers:
        return JsonResponse({"status": "running", "workers": list(active_workers.keys())})
    else:
        return JsonResponse({"status": "stopped", "workers": []}, status=503)

# MAIN PAGE ************************************************************************************************************
def main_page_react(request):
    return render(request, 'index.html')

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    logout(request)
    return JsonResponse({'response': 'User logged out!'}, safe=False)

@csrf_exempt
def register(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        user_name = request_data["user_name"]
        if User.objects.filter(username=user_name).exists():
            return JsonResponse({'response': 'User already exists'}, safe=False)
        elif User.objects.filter(email=request_data["email"]).exists():
            return JsonResponse({'response': 'Email already exists'}, safe=False)
        else:
            user = User.objects.create_user(username=user_name,
                                           password=request_data["password"],
                                           email=request_data["email"])
            user.save()
            Portfolio(portfolio_name='Main Portfolio',
                      portfolio_code='MAIN_' + user_name.upper(),
                      portfolio_type='Main',
                      status="active",
                      inception_date=date.today(),
                      owner=user_name).save()
            return JsonResponse({'response': 'Succesfull registration'}, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensures only authenticated users can access this
def change_password(request):
    user = request.user  # Get the authenticated user
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # 1. Check if the old password is correct
        if not user.check_password(old_password):  # ✅ Correct usage
            return JsonResponse({"error": "Old password is incorrect."}, status=400)

        # 2. Ensure new password is different from the old one
        if old_password == new_password:
            return JsonResponse({"error": "New password cannot be the same as the old password."}, status=400)

        # 3. Check password length and strength
        if len(new_password) < 6:
            return JsonResponse({"error": "New password must be at least 6 characters long."}, status=400)

        # 4. Successfully change the password
        user.set_password(new_password)
        user.save()

        return JsonResponse({"message": "Password changed successfully!"}, status=200)

    # If serializer validation fails, return the first error message
    return JsonResponse({"error": next(iter(serializer.errors.values()))[0]}, status=400)






@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    user = request.user  # Get the authenticated user
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime
    }
    return JsonResponse(user_data, safe=False)














