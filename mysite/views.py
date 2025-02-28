import json
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import logout
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer
from .registerSerializer import RegisterSerializer
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

@api_view(['POST'])
def register_user(request):
    """
    Handle user registration and return JWT tokens (access and refresh tokens)
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return JsonResponse({
            'refresh': str(refresh),
            'access': str(access_token),
        }, status=201)

    return JsonResponse(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensures only authenticated users can access this
def change_password(request):
    user = request.user  # Get the authenticated user
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # 1️⃣ Check if the old password is correct
        if not user.check_password(old_password):
            return JsonResponse({"error": "Old password is incorrect."}, status=400)

        # 2️⃣ Ensure new password is different from old password
        if old_password == new_password:
            return JsonResponse({"error": "New password cannot be the same as the old password."}, status=400)

        # 3️⃣ Validate the new password using Django's built-in password validator
        try:
            validate_password(new_password, user)  # Only validate the new password
        except ValidationError as e:
            # If validation fails, return the error message
            return JsonResponse({"error": e.messages}, status=400)

        # 4️⃣ Successfully change the password
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














