from rest_framework import serializers
from .models import BrokerAccounts

class BrokerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerAccounts
        fields = '__all__'