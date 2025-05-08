from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView, 
    TokenVerifyView
)
jwt_urls = [
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("access/", TokenVerifyView.as_view(), name="token_verify"),
]

urlpatterns = jwt_urls