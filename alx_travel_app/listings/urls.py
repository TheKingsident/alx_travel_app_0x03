from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, PaymentViewSet, api_root

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('v1/', include(router.urls)),
]
