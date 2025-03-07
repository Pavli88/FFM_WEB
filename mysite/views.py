import json
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .changePasswordSerializer import ChangePasswordSerializer
from .registerSerializer import RegisterSerializer
from mysite.tasks import long_running_task
from mysite.celery import app
from mysite.models import UserProfile
from .resetPasswordSerializer import ResetPasswordConfirmSerializer
from rest_framework.views import APIView
from .validators import CustomPasswordValidator


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


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return JsonResponse({"detail": "Username and password are required"}, status=400)

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    if not user.is_active:
        return JsonResponse({"detail": "User account is disabled"}, status=403)

    refresh = RefreshToken.for_user(user)

    return JsonResponse({
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    })

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
def forgot_password(request):
    email = request.data.get('email')

    if not email:
        return JsonResponse({"detail": "Email is required"}, status=400)

    try:
        # Get the user object
        user = User.objects.get(email=email)

        # Get or create the associated user profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        # Generate a reset token and store it in the UserProfile
        reset_token = get_random_string(30)  # Generate a random token
        user_profile.reset_token = reset_token
        user_profile.token_created_at = timezone.now()  # Save the token creation time
        user_profile.save()

        # Create the reset link
        reset_link = f"{settings.FRONTEND_URL}/reset_password/{reset_token}"

        # Send the reset email
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            "no-reply@example.com",
            [email],
            fail_silently=False,
        )

        return JsonResponse({"detail": "Password reset link sent"}, status=200)

    except User.DoesNotExist:
        return JsonResponse({"detail": "User with this email does not exist"}, status=404)

@api_view(['POST'])
def reset_password(request, reset_token):
    try:
        # Find the UserProfile by the reset token
        user_profile = UserProfile.objects.get(reset_token=reset_token)

        # Check if the token is valid and not expired
        if not user_profile.reset_token or user_profile.reset_token != reset_token:
            return JsonResponse({"detail": "Invalid or expired reset token"}, status=400)

        # Optionally, check if the token has expired (e.g., 1 hour expiration)
        if (timezone.now() - user_profile.token_created_at).total_seconds() > 3600:  # 1 hour
            return JsonResponse({"detail": "Reset token has expired"}, status=400)

        # Get the new password from the request and validate it using the serializer
        serializer = ResetPasswordConfirmSerializer(data=request.data)

        if serializer.is_valid():
            # If the password is valid, save the new password for the user
            new_password = serializer.validated_data['new_password']

            # Update the user's password
            user = user_profile.user  # Access the related user object
            user.set_password(new_password)
            user.save()

            # Clear the reset token and timestamp after successful password reset
            user_profile.reset_token = None
            user_profile.token_created_at = None
            user_profile.save()

            return JsonResponse({"detail": "Password reset successfully"}, status=200)
        else:
            return JsonResponse({"error": next(iter(serializer.errors.values()))}, status=400)
    except UserProfile.DoesNotExist:
        return JsonResponse({"detail": "Invalid or expired reset token"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    logout(request)
    return JsonResponse({'response': 'User logged out!'}, safe=False)

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














