from rest_framework.permissions import AllowAny
from rest_framework.views import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin

from core.utils import APIResponse, hash_code
from core.services import send_reset_password_email, logToSlack, send_verification_email
from core.models import Token, ActivityLog
from wallet.models import Wallet, Transaction

from .models import User, Profile, Address, EmailOTP

from .serializers import (
    UserRegisterSerializer,
    VerifyEmailSerializer,
    LoginSerializer,
    ProfileSerializer,
    ResetPasswordSerializer,
    AddressSerializer,
    ResendEmailSerializer,
)
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404


from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from simba.permissions import IsValidUser
from wallet.serializers import WalletSerializer, TransactionSerializer
from django.db.models.functions import TruncDate
from random import randint


# Create your views here.
class UserRegisterViewSet(GenericViewSet, APIResponse):
    """
    User registration endpoint.
    Only supports POST /api/register
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    authentication_classes = []
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success(
            message="User created",
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailViewset(GenericViewSet, APIResponse):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = VerifyEmailSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        serializer.save()
        refresh = RefreshToken.for_user(user)

        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = request.META.get("REMOTE_ADDR", "Unknown")

        refresh["email"] = user.email
        refresh["user_type"] = user.user_type
        refresh["user_agent"] = user_agent
        refresh["ip_address"] = ip_address

        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return self.success(
            message="Email verified successfully",
            status=status.HTTP_200_OK,
            data={"email": user.email, "role": user.user_type, "tokens": tokens},
        )


class ResendEmailViewSet(GenericViewSet, APIResponse):
    """ """

    permission_classes = [AllowAny]
    serializer_class = ResendEmailSerializer
    authentication_classes = []
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # generate OTP code
        otp = randint(100000, 999999)

        # store OTP code
        EmailOTP.objects.create(
            code_hash=hash_code(str(otp)),
            user=user,
            is_active=True,  #
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        # send OTP code; sendgrid
        send_verification_email(user.email, otp)

        return self.success(
            message="Email resent",
            status=status.HTTP_201_CREATED,
        )


class LoginViewset(GenericViewSet, APIResponse):
    """
    Authenticates a user using their credentials,
    and sets a token in an HttpOnly cookie
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = request.META.get("REMOTE_ADDR", "Unknown")

        refresh["email"] = user.email
        refresh["user_type"] = user.user_type
        refresh["user_agent"] = user_agent
        refresh["ip_address"] = ip_address

        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        # response.set_cookie(
        # 	key="session_id",
        # 	value=request.session.session_key,
        # 	httponly=True,
        # 	secure=True,
        # 	samesite="None",
        # 	max_age=
        # )

        return self.success(
            message="Login successful",
            status=status.HTTP_200_OK,
            data={"email": user.email, "role": user.user_type, "tokens": tokens},
        )


class ForgotPasswordViewset(GenericViewSet, APIResponse):
    """
    Initiates a password reset
    Checks email and sends token
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request):
        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = request.META.get("REMOTE_ADDR", "Unknown")
        email = request.data.get("email")

        user = get_object_or_404(User, email=email, is_valid=True)

        # create reset token
        token = Token.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(minutes=1),
            category="password_reset",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        # send email to user

        reset_link = f"https://simba.com/reset-password?token={token.token}"
        send_reset_password_email(to_email=user.email, reset_link=reset_link)

        return self.success(
            message="Reset password initiation successful",
            status=status.HTTP_200_OK,
        )


class ResetPasswordViewset(GenericViewSet, APIResponse):
    """
    Confirms reset token, updates password
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        new_password = validated_data.get("password")
        payload_token = validated_data.get("token")

        if not new_password or not payload_token:
            return self.error(message="Password/Token field is required")

        token_match = Token.objects.filter(
            token=payload_token,
            expires_at__gt=timezone.now(),
            category="password_reset",
            used=False,
            is_active=True,
        )

        if token_match.exists():
            with transaction.atomic():
                token = token_match.first()

                # update password
                user = token.user
                user.set_password(new_password)
                user.save()

                # invalidate all existing password_reset tokens
                Token.objects.filter(
                    user=user,
                    category="password_reset",
                    used=False,
                    is_active=True,
                ).update(is_active=False, used=True)

                # log action
                ActivityLog.objects.create(
                    user=user,
                    category="password_reset",
                    description="User reset password",
                    metadata={
                        "user_agent": token.user_agent,
                        "ip_address": token.ip_address,
                        "token_id": token.id,
                        "token_token": str(token.token),
                    },
                )

                return self.success(message="Password reset successfully")
        else:
            return self.error(message="Invalid token", status=status.HTTP_404_NOT_FOUND)

        return self.success(
            message="Login successful",
            status=status.HTTP_200_OK,
            data={"email": user.user_type, "role": user.user_type, "tokens": tokens},
        )


class LogoutViewSet(GenericViewSet, APIResponse):
    permission_classes = [IsAuthenticated, IsValidUser]

    def create(self, request):
        token = request.data["refresh"]
        refresh = RefreshToken(token)
        refresh.blacklist()

        return self.success(message="Logged out successfully.")


class ProfileView(APIView, APIResponse):
    """
    Get & Update Profile Info
    """

    permission_classes = [IsAuthenticated, IsValidUser]

    def get(self, request):
        user = request.user

        profile = get_object_or_404(Profile, user=user)
        serializer = ProfileSerializer(profile)

        return self.success(
            message="Success",
            data={
                **serializer.data,
            },
        )

    def patch(self, request):
        user = request.user

        profile = get_object_or_404(Profile, user=user)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success(
            message="Profile updated successfully", data=serializer.data
        )


class AddressViewSet(ModelViewSet, APIResponse):
    permission_classes = [IsAuthenticated, IsValidUser]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request):
        qs = self.get_queryset()
        serializer = AddressSerializer(qs, many=True)
        return self.success(
            message="Addresses loaded successfully", data=serializer.data
        )