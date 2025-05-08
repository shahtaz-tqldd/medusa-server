from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView, 
    TokenVerifyView
)
jwt_urls = [
    path("access/", TokenVerifyView.as_view(), name="token_verify"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns = jwt_urls