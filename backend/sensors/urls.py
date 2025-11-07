from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CropAlertViewSet, SensorWebhookView

router = DefaultRouter()
router.register(r"crop/alerts", CropAlertViewSet, basename="crop-alert")

urlpatterns = [
    path("webhook/", SensorWebhookView.as_view(), name="sensor-webhook"),
    path("", include(router.urls)),
]
