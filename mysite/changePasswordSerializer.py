from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=6)

    def validate_new_password(self, value):
        """Validate password strength using Django's built-in validators"""
        validate_password(value)  # Enforces strong password rules
        return value
