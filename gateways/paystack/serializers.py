from rest_framework import serializers

from gateways.paystack.models import PaystackTransaction


class PaymentSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True)
    amount = serializers.IntegerField(required=True, min_value=1)


class PaystackTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaystackTransaction
        fields = "__all__"
