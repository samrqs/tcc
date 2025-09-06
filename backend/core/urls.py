from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/chatbot/", include("chatbot.urls")),
    path("api/sensors/", include("sensors.urls")),
]
