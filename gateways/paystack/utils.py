import logging

import requests
from django.conf import settings

from gateways.paystack.exceptions import PaymentErrorException

logger = logging.getLogger(__name__)


class PaystackPaymentGateway:
    def headers(self):
        try:
            access_token = settings.PAYSTACK_SECRET_KEY
            header = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            return header
        except Exception as e:
            logger.error(f"Error getting header: {e}")
            return None

    def initialize_payment(self, amount, email, metadata=None):
        try:
            data = {"amount": float(amount) * 100, "email": email, "metadata": metadata}
            payment_url = "https://api.paystack.co/transaction/initialize"
            response = requests.post(payment_url, headers=self.headers(), json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error making payment: {e}")
            raise PaymentErrorException(str(e))

    def verify_payment(self, reference):
        try:
            verification_url = "https://api.paystack.co/transaction/verify"
            response = requests.get(f"{verification_url}/{reference}", headers=self.headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            raise PaymentErrorException(str(e))
