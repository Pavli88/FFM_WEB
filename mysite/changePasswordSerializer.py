from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        """Validate password strength using Django's built-in validators, including CustomPasswordValidator."""
        validate_password(value)  # ✅ Includes all password validators from settings.py
        return value
