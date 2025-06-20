import logging

import requests
from django.conf import settings

from gateways.paystack.exceptions import PaymentErrorException

logger = logging.getLogger(__name__)


class PaystackPaymentGateway:
    """
    A service class to handle Paystack payment operations such as initializing and verifying payments.
    """

    def headers(self):
        """
        Constructs the headers required for Paystack API requests.

        Returns:
            dict: A dictionary containing the authorization and content-type headers.
                  Returns None if an error occurs during header construction.
        """
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
        """
        Initiates a payment transaction using Paystack.

        Args:
            amount (float or int): The amount to be charged (in base currency).
            email (str): The customer's email address.
            metadata (dict, optional): Additional metadata to attach to the transaction.

        Returns:
            dict: The JSON response from Paystack containing transaction details.

        Raises:
            PaymentErrorException: If the API request fails or returns an error.
        """
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
        """
        Verifies the status of a Paystack transaction using its reference.

        Args:
            reference (str): The unique transaction reference to verify.

        Returns:
            dict: The JSON response from Paystack containing the verification result.

        Raises:
            PaymentErrorException: If the verification request fails or returns an error.
        """
        try:
            verification_url = "https://api.paystack.co/transaction/verify"
            response = requests.get(f"{verification_url}/{reference}", headers=self.headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            raise PaymentErrorException(str(e))
