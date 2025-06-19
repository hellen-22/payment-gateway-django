from rest_framework.routers import DefaultRouter

from gateways.paystack.views import PaystackPaymentVerificationViewSet, PaystackPaymentViewSet

router = DefaultRouter()
router.register(r"payment", PaystackPaymentViewSet, basename="paystack-payment")
router.register(r"callback", PaystackPaymentVerificationViewSet, basename="paystack-verification")


urlpatterns = router.urls
