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
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout, login, authenticate

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
def logout_user(request):

    print("===========")
    print("USER LOGOUT")
    print("===========")
    print("Redirecting to logout page")

    logout(request)
    return JsonResponse({'response': 'User logged out!'}, safe=False)


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body.decode('utf-8'))
            username = request_data.get("username")
            password = request_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Serialize the user data
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "date_joined": user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
                }

                return JsonResponse({'userAllowedToLogin': True, 'user': user_data}, safe=False)

            return JsonResponse({'response': 'User is not registered in the database!'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


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


@csrf_exempt
def change_password(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            current_password = data.get("current_password")
            new_password = data.get("new_password")

            user = request.user
            if not user.check_password(current_password):
                return JsonResponse({"error": "Current password is incorrect"}, status=400)

            user.set_password(new_password)
            user.save()

            return JsonResponse({"message": "Password changed successfully"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
















