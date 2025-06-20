from unittest import TestCase
from unittest.mock import MagicMock, patch

from gateways.paystack.exceptions import PaymentErrorException
from gateways.paystack.utils import PaystackPaymentGateway


class PaystackGatewayTestSetUp(TestCase):
    def setUp(self):
        self.gateway = PaystackPaymentGateway()
        self.amount = 1000
        self.email = "test@example.com"
        self.metadata = {"name": "Test User"}
        self.reference = "test_reference_12345"


class TestInitializePayment(PaystackGatewayTestSetUp):
    @patch("gateways.paystack.utils.requests.post")
    def test_initialize_payment_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "authorization_url": "https://paystack.com/redirect",
                "reference": self.reference,
                "access_code": "access_code_abc",
            },
        }
        mock_post.return_value = mock_response

        res = self.gateway.initialize_payment(self.amount, self.email, self.metadata)

        self.assertTrue(res["status"])
        self.assertIn("authorization_url", res["data"])
        self.assertEqual(res["data"]["reference"], self.reference)

    @patch("gateways.paystack.utils.requests.post")
    def test_initialize_payment_failure_raises_custom_exception(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Payment failed")
        mock_post.return_value = mock_response

        with self.assertRaises(PaymentErrorException) as context:
            self.gateway.initialize_payment(self.amount, self.email, self.metadata)

        self.assertIn("Payment failed", str(context.exception))


class TestVerifyPayment(PaystackGatewayTestSetUp):
    @patch("gateways.paystack.utils.requests.get")
    def test_verify_payment_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": True, "data": {"reference": self.reference, "status": "success"}}
        mock_get.return_value = mock_response

        res = self.gateway.verify_payment(self.reference)

        self.assertTrue(res["status"])
        self.assertEqual(res["data"]["status"], "success")
        self.assertEqual(res["data"]["reference"], self.reference)

    @patch("gateways.paystack.utils.requests.get")
    def test_verify_payment_failure_raises_custom_exception(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Verification failed")
        mock_get.return_value = mock_response

        with self.assertRaises(PaymentErrorException) as context:
            self.gateway.verify_payment(self.reference)

        self.assertIn("Verification failed", str(context.exception))
