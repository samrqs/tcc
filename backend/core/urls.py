from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from auth.views import EmailTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ht/", include("health_check.urls")),
    path("", include("django_prometheus.urls")),
    path("api/chatbot/", include("chatbot.urls")),
    path("api/sensors/", include("sensors.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema")),
    path('api/users/', include('users.urls')),
    path("api/auth/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh")
]
