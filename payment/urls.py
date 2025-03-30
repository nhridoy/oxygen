from rest_framework.routers import DefaultRouter

from payment.views import (
    GetSavedCardViewSet,
    MakePaymentViewSet,
)

router = DefaultRouter()

# Authorize Payment
router.register(r"make-payment", MakePaymentViewSet, basename="make-payment")
router.register(r"get-saved-cards", GetSavedCardViewSet, basename="get-saved-cards")


urlpatterns = []
urlpatterns += router.urls
