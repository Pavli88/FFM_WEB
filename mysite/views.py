import json
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
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
import os
from mysite.models import UserProfile
from .resetPasswordSerializer import ResetPasswordConfirmSerializer
from .UserSerializer import UserSerializer
from .models import Follow

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
def register_user(request):
    print('request', request)
    """
    Handle user registration and store JWT tokens in HTTPOnly cookies
    """
    serializer = RegisterSerializer(data=request.data)
    print('serializer: ', serializer)


    if serializer.is_valid():
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Create response and set HTTPOnly Secure cookies
        response = JsonResponse({"detail": "Registration successful"}, status=201)
        response.set_cookie("access", str(access_token), httponly=True, secure=True, samesite='Lax')
        response.set_cookie("refresh", str(refresh), httponly=True, secure=True, samesite='Lax')

        return response
    print('serializer errors: ', serializer.errors)
    print('type: ',type(serializer.errors))
    return JsonResponse(serializer.errors, status=400)


# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def login_user(request):

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return JsonResponse({"detail": "Username and password are required"}, status=400)

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({"detail": "Invalid username or password"}, status=401)

    if not user.is_active:
        return JsonResponse({"detail": "User account is disabled"}, status=403)

    refresh = RefreshToken.for_user(user)

    response = JsonResponse({"detail": "Login successful"})
    response.set_cookie(
        "access_token",
        str(refresh.access_token),
        httponly=True,
        secure=True, # Productionbe ez True
        samesite='None')
    response.set_cookie(
        "refresh_token",
        str(refresh),
        httponly=True,
        secure=True,
        samesite='None')

    return response

@api_view(['POST'])
def logout_user(request):
    response = JsonResponse({"detail": "Logout successful"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')

    if not email:
        return JsonResponse({"detail": "Email is required"}, status=400)

    # Always return a success response to prevent email enumeration attacks
    response_message = {"detail": "If an account with this email exists, a password reset link has been sent."}

    try:
        user = User.objects.get(email=email)

        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        # Generate reset token & store it
        reset_token = get_random_string(30)
        user_profile.reset_token = reset_token
        user_profile.token_created_at = timezone.now()  # Save the time for expiry check later
        user_profile.save()

        # Generate reset link
        reset_link = f"{settings.FRONTEND_URL}/reset_password/{reset_token}"

        # Send reset email
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,  # Use configured email
            [email],
            fail_silently=False,
        )

    except User.DoesNotExist:
        pass  # Prevent leaking valid emails

    return JsonResponse(response_message, status=200)

@api_view(['POST'])
def reset_password(request, reset_token):
    try:
        # Find the UserProfile by the reset token
        user_profile = UserProfile.objects.get(reset_token=reset_token)

        # Check if the token is valid and not expired using the method in UserProfile
        if not user_profile.is_reset_token_valid():
            return JsonResponse({"detail": "Invalid or expired reset token"}, status=400)

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_email(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    try:
        # Extract email from request data
        new_email = request.data.get("email")

        if not new_email:
            return JsonResponse({"error": "Email is required."}, status=400)

        # Validate email format
        try:
            validate_email(new_email)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)  # Properly return validation error message

        # Check if email already exists
        if User.objects.filter(email=new_email).exists():
            return JsonResponse({"error": "Email is already in use."}, status=400)

        # Update email
        user = request.user
        user.email = new_email
        user.save()

        return JsonResponse({"detail": "Email updated successfully."}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    try:
        user = request.user
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        image_url = request.build_absolute_uri(user_profile.image.url) if user_profile.image else None
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            'image_url': image_url,
            "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            "followers_count": user.followers.count(),
            "following_count": user.following.count(),
        }
        return JsonResponse(user_data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=401)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    """Allows users to upload a profile picture"""
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)

    image = request.FILES['image']

    # Delete old image if exists
    if user_profile.image:
        old_image_path = os.path.join(settings.MEDIA_ROOT, str(user_profile.image))
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

    user_profile.image = image
    user_profile.save()
    return JsonResponse({'message': 'Profile picture updated successfully', 'image_url': user_profile.image.url})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_picture(request):
    """Allows users to delete their profile picture"""
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if not user_profile.image:
        return JsonResponse({'error': 'No profile picture to delete'}, status=400)

    image_path = os.path.join(settings.MEDIA_ROOT, str(user_profile.image))
    if os.path.exists(image_path):
        os.remove(image_path)

    user_profile.image = None
    user_profile.save()

    return JsonResponse({'message': 'Profile picture deleted successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        try:
            serializer.save()
            return JsonResponse({"message": "Profile updated successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # If serializer validation fails, return the first error message
    return JsonResponse({"error": next(iter(serializer.errors.values()))[0]}, status=400)

@api_view(['GET'])
def public_user_profile(request, username):
    try:
        user = User.objects.get(username=username)
        data = {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined,
            "image_url": user.profile.image.url if hasattr(user, 'profile') and user.profile.image else None,
            "followers_count": user.followers.count(),
            "following_count": user.following.count(),
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    try:
        user_to_follow = User.objects.get(username=username)
        if user_to_follow == request.user:
            return JsonResponse({"error": "You can't follow yourself."}, status=400)

        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        return JsonResponse({"message": f"You are now following {username}."})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    try:
        user_to_unfollow = User.objects.get(username=username)
        Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
        return JsonResponse({"message": f"You have unfollowed {username}."})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_following(request, username):
    try:
        user = User.objects.get(username=username)
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        return JsonResponse({"is_following": is_following})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
