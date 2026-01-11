import random
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_205_RESET_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_401_UNAUTHORIZED,
)

from base.helpers.response import APIResponse

from user.models import PasswordResetOTP
from user.v1.serializers import (
    CreateUserSerializer,
    LoginSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    UserDetailsSerializer,
)

from user.v1.res_msg import (
    USER_REGISTER,
    USER_LOGIN,
    USER_TOKEN_REFRESH,
    USER_DETAILS,
    USER_UPDATE,
    USER_FORGOT_PASSWORD,
    USER_RESET_PASSWORD
)

User = get_user_model()

class CreateNewUser(generics.CreateAPIView):
    """
    APIView to create New User with secret api key
    """
    RESPONSE_LANGUAGE = "en"
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user_data = UserDetailsSerializer(user).data

        return APIResponse.success(
            data = user_data, 
            message = USER_REGISTER[self.RESPONSE_LANGUAGE], 
            status = HTTP_201_CREATED
        )


class Login(generics.GenericAPIView):
    serializer_class = LoginSerializer
    RESPONSE_LANGUAGE = "en"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.context["access_token"]
        refresh_token = serializer.context["refresh_token"]

        response = APIResponse.success(
            message=USER_LOGIN[self.RESPONSE_LANGUAGE],
        )

        IS_PROD = not settings.DEBUG

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=IS_PROD,
            samesite="None" if IS_PROD else "Lax",
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=IS_PROD,
            samesite="None" if IS_PROD else "Lax",
            path="/",
        )

        return response



class RefreshToken(TokenRefreshView):
    RESPONSE_LANGUAGE = "en"

    def post(self, request, *args, **kwargs):
        # Try to get from cookie first, then from body
        refresh_token = request.COOKIES.get("refresh_token") or request.data.get("refresh")

        if not refresh_token:
            return APIResponse.error(
                "Refresh token missing",
                status=HTTP_401_UNAUTHORIZED
            )

        # Inject refresh token into request data
        request.data["refresh"] = refresh_token

        jwt_response = super().post(request, *args, **kwargs)

        access_token = jwt_response.data.get("access")
        new_refresh_token = jwt_response.data.get("refresh")

        response = APIResponse.success(
            message=USER_TOKEN_REFRESH[self.RESPONSE_LANGUAGE],
            data={
                "access_token": access_token,
                "refresh_token": new_refresh_token,
            }
        )

        IS_PROD = not settings.DEBUG

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=IS_PROD,
            samesite="None" if IS_PROD else "Lax",
            path="/",
            max_age=60 * 5,
        )

        if new_refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                secure=IS_PROD,
                samesite="None" if IS_PROD else "Lax",
                path="/",
                max_age=60 * 60 * 24 * 7,
            )

        return response


class UserDetails(generics.GenericAPIView):
    """
    API View to fetch user details
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserDetailsSerializer

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)

        return APIResponse.success(
            data=serializer.data, 
            message = USER_DETAILS[self.RESPONSE_LANGUAGE], 
        )


class UpdateUserDetails(generics.UpdateAPIView):
    """
    API view to update user details
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserDetailsSerializer

    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return APIResponse.success(
            data=serializer.data,
            message = USER_UPDATE[self.RESPONSE_LANGUAGE], 
            status=HTTP_205_RESET_CONTENT,
        )


class ForgotPassword(generics.GenericAPIView):
    """
    API view to receive request for forget password and send otp to email
    """
    RESPONSE_LANGUAGE = "en"
    serializer_class = ForgetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return APIResponse.error(
                message="User does not exist with this email", status=HTTP_404_NOT_FOUND
            )

        otp = str(random.randint(1000, 9999))

        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_mail(
            subject="Your password reset OTP",
            message=f"Hey {user.first_name}, Your otp for password reset is {otp} and validity is 10 minutes",
            from_email="",
            recipient_list=[email],
            fail_silently=False,
        )

        return APIResponse.success(message = USER_FORGOT_PASSWORD[self.RESPONSE_LANGUAGE])


class ResetPassword(generics.GenericAPIView):
    """
    API view to reset password with otp
    """
    RESPONSE_LANGUAGE = "en"
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serialzier = self.get_serializer(data=request.data)
        serialzier.is_valid(raise_exception=True)

        email = serialzier.validated_data["email"]
        otp = serialzier.validated_data["otp"]
        new_password = serialzier.validated_data["new_password"]
        confirm_password = serialzier.validated_data["confirm_password"]

        if new_password != confirm_password:
            return APIResponse.error(
                message="Password did not match!", status=HTTP_409_CONFLICT
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return APIResponse.error(
                message="User does not exist with this email", status=HTTP_404_NOT_FOUND
            )

        otp_entry = PasswordResetOTP.objects.filter(user=user, otp=otp).last()

        if not otp_entry or not otp_entry.is_valid():
            return APIResponse.error(message="Invalid or expired OTP")

        user.set_password(new_password)
        user.save()

        otp_entry.delete()

        return APIResponse.success(message = USER_RESET_PASSWORD[self.RESPONSE_LANGUAGE])
