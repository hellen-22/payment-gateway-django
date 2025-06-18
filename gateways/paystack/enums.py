from django.db import models


class PaystackPaymentStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    ABANDONED = "abandoned", "Abandoned"
    PENDING = "pending", "Pending"
