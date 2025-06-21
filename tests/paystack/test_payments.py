from unittest.mock import patch

from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from gateways.paystack.exceptions import PaymentErrorException
from gateways.paystack.models import PaystackTransaction


class PaystackBaseTestSetUp(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.transaction = baker.make(PaystackTransaction)
        self.reference = "1gh2j3k4l5m6n7o8p9q0r"
        self.current_count = PaystackTransaction.objects.count()

        self.payment_url = reverse("paystack-payment-list")
        self.retrieve_url = reverse("paystack-payment-detail", kwargs={"reference": self.transaction.reference})
        self.verify_url = reverse("paystack-verification-verify-payment", kwargs={"reference": self.reference})


class TestMakePaystackPayment(PaystackBaseTestSetUp):

    def setUp(self):
        super().setUp()

        self.payment_data = {
            "name": "Test User",
            "email": "testemail@email.com",
            "amount": 1000,
        }

    @patch("gateways.paystack.views.PaystackPaymentGateway.initialize_payment")
    def test_make_payment_success(self, mock_initialize_payment):
        mock_initialize_payment.return_value = {
            "status": True,
            "message": "Message",
            "data": {
                "authorization_url": "https://paystack.com/redirect",
                "reference": "ref_12345",
                "access_code": "access_12345",
            },
        }

        response = self.client.post(self.payment_url, self.payment_data)

        mock_initialize_payment.assert_called_once_with(
            amount=self.payment_data["amount"],
            email=self.payment_data["email"],
            metadata={"name": self.payment_data["name"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("authorization_url", response.data["data"])
        self.assertEqual(response.data["status"], True)

    @patch("gateways.paystack.views.PaystackPaymentGateway.initialize_payment")
    def test_make_payment_failure(self, mock_initialize_payment):
        mock_initialize_payment.side_effect = PaymentErrorException("Payment initialization failed")

        response = self.client.post(self.payment_url, self.payment_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Payment initialization failed")

    def test_if_amount_is_less_than_1_returns_400(self):
        self.payment_data["amount"] = 0
        response = self.client.post(self.payment_url, self.payment_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ensure this value is greater than or equal to 1", str(response.data["amount"]))

    def test_if_email_is_invalid_returns_400(self):
        self.payment_data["email"] = "invalid-email"
        response = self.client.post(self.payment_url, self.payment_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Enter a valid email address.", str(response.data["email"]))

    def test_if_name_is_empty_returns_400(self):
        self.payment_data["name"] = ""
        response = self.client.post(self.payment_url, self.payment_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", str(response.data["name"]))


class TestRetrievePaystackTransaction(PaystackBaseTestSetUp):
    def setUp(self):
        super().setUp()

    def test_retrieve_transaction_success(self):
        response = self.client.get(self.retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reference"], self.transaction.reference)
        self.assertEqual(response.data["customer_email"], self.transaction.customer_email)

    def test_retrieve_transaction_not_found(self):
        invalid_url = reverse("paystack-payment-detail", kwargs={"reference": "invalid_reference"})
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestVerifyPaystackPayment(PaystackBaseTestSetUp):
    def setUp(self):
        super().setUp()

    @patch("gateways.paystack.views.PaystackPaymentGateway.verify_payment")
    def test_verify_payment_success(self, mock_verify_payment):
        mock_verify_payment.return_value = {
            "data": {
                "status": "success",
                "customer": {"email": "test@email.com"},
                "metadata": {"name": "Test User"},
                "amount": self.transaction.amount * 100,
                "gateway_response": "Payment successful",
            }
        }

        response = self.client.get(self.verify_url)

        mock_verify_payment.assert_called_once_with(self.reference)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(PaystackTransaction.objects.count(), self.current_count + 1)

    @patch("gateways.paystack.views.PaystackPaymentGateway.verify_payment")
    def test_if_status_is_not_success_does_not_create_transaction(self, mock_verify_payment):
        mock_verify_payment.return_value = {
            "data": {
                "status": "failed",
                "customer": {"email": "test1@email.com"},
                "metadata": {"name": "Test User 1"},
                "amount": self.transaction.amount * 100,
                "gateway_response": "Payment failed",
            }
        }

        response = self.client.get(self.verify_url)

        mock_verify_payment.assert_called_once_with(self.reference)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(PaystackTransaction.objects.count(), self.current_count)

    @patch("gateways.paystack.views.PaystackPaymentGateway.verify_payment")
    def test_verify_payment_failure(self, mock_verify_payment):
        mock_verify_payment.side_effect = PaymentErrorException("Verification failed")

        response = self.client.get(self.verify_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Verification failed")
        self.assertEqual(PaystackTransaction.objects.count(), self.current_count)
