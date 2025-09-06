from django.urls import path

from .views import ChatbotWebhookView

urlpatterns = [
    path("webhook", ChatbotWebhookView.as_view(), name="chatbot-webhook"),
]
