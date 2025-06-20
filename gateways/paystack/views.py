from rest_framework import decorators, response, status, viewsets

from gateways.paystack.exceptions import PaymentErrorException
from gateways.paystack.models import PaystackTransaction
from gateways.paystack.serializers import PaymentSerializer, PaystackTransactionSerializer
from gateways.paystack.utils import PaystackPaymentGateway


class PaystackPaymentViewSet(viewsets.ViewSet):
    """
    Handling Paystack payment operations.

    This endpoint allows you to create a payment by providing the customer's name, email, and the amount to be charged.
    """

    def create(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_gateway = PaystackPaymentGateway()
        try:
            res = payment_gateway.initialize_payment(
                amount=serializer.validated_data["amount"],
                email=serializer.validated_data["email"],
                metadata={"name": serializer.validated_data["name"]},
            )

            return response.Response(res, status=status.HTTP_200_OK)
        except PaymentErrorException as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific Paystack transaction by its reference.
        """
        try:
            transaction = PaystackTransaction.objects.get(reference=pk)
            serializer = PaystackTransactionSerializer(transaction)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except PaystackTransaction.DoesNotExist:
            return response.Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)


class PaystackPaymentVerificationViewSet(viewsets.ViewSet):
    """
    Handling Paystack payment verification operations.

    This endpoint allows you to verify a payment by providing the transaction reference.
    """

    @decorators.action(detail=False, methods=["get"], url_path="(?P<reference>[^/.]+)")
    def verify_payment(self, request, reference=None):
        payment_gateway = PaystackPaymentGateway()
        try:
            res = payment_gateway.verify_payment(reference)
            response_data = res.get("data", {})
            data = {
                "status": response_data.get("status"),
                "email": response_data.get("customer", {}).get("email"),
                "name": response_data.get("metadata", {}).get("name"),
                "amount": response_data.get("amount") / 100,
                "message": response_data.get("gateway_response"),
            }

            if data["status"] == "success":
                PaystackTransaction.objects.update_or_create(
                    reference=reference,
                    defaults={
                        "customer_email": data["email"],
                        "customer_name": data["name"],
                        "amount": data["amount"],
                        "status": data["status"],
                    },
                )
            return response.Response(data, status=status.HTTP_200_OK)
        except PaymentErrorException as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
