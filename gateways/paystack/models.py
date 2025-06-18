from django.db import models

from gateways.common.models import AbstractBaseModel
from gateways.paystack.enums import PaystackPaymentStatus


class PaystackTransaction(AbstractBaseModel):
    """
    Model to store Paystack transaction details.
    """

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PaystackPaymentStatus.choices, default=PaystackPaymentStatus.PENDING
    )
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Transaction {self.reference} - {self.status}"
