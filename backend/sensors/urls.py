from django.urls import path

from .views import SensorWebhookView

urlpatterns = [
    path("webhook", SensorWebhookView.as_view(), name="sensor-webhook"),
]
