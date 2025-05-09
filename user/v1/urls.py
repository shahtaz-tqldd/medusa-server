from django.urls import path
from .views import (
    CreateNewUser,
    Login,
    RefreshToken,
    UserDetails,
    UpdateUserDetails,
    ForgotPassword,
    ResetPassword
)

app_name = 'auth'

urlpatterns = [
    path("register/", CreateNewUser.as_view(), name="create-user"),
    path("login/", Login.as_view(), name="login"),
    path("token-refresh/", RefreshToken.as_view(), name="token-refresh"),
    path("user-details/", UserDetails.as_view(), name="user-details"),
    path("user-details/update/", UpdateUserDetails.as_view(), name="update-user"),
    path("forget-password/", ForgotPassword.as_view(), name="forget-password"),
    path("reset-password/", ResetPassword.as_view(), name="reset-password"),
]
