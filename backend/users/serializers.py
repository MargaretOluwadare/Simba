import logging
import re
from random import randint

from decouple import config
from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import authenticate

from core.services import logToSlack, send_verification_email, upload_to_cloudinary

from .models import EmailOTP, User, Profile, Address
from core.utils import hash_code
from simba.response import APIResponse
from datetime import timedelta
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]

        extra_kwargs = {
            "email": {"required": True},
            "password": {"write_only": True, "required": True},
        }

    def validate_email(self, value):
        # ensure email does not exist
        logger.info(f"Email: {value}")
        logger.info(User.objects.filter(email=value))
        if User.objects.filter(email=value).exists():
            response = APIResponse
            raise serializers.ValidationError(
                "A user with this email address already exists"
            )

        return value

    def validate_password(self, value):
        # check if password length is greater than 8
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must contain at least 8 characters"
            )
        # check if password contains special characters
        if not re.search(r"[!@#$%^&*.]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character"
            )
        # check if password contains uppercase characters
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase character"
            )

        # check if password contains lowercase characters
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase character"
            )

        # check if password contains digits
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase character"
            )

        return value

    def create(self, validated_data):
        with transaction.atomic():
            # create user record
            email = validated_data["email"]
            password = validated_data["password"]

            email_prefix = email.split("@")
            username = f"{email_prefix[0]}{get_random_string(6)}"

            user = User.objects.create(
                email=email,
                user_type="customer",
                username=username,
            )

            user.set_password(password)
            user.save()

            Profile.objects.create(user=user)

            # log user to SLACK channel
            slack_url = config("ACCOUNT_CREATION_SLACK_URL")
            payload = {
                "text": f":partying_face: Another reason we're still in business\nNew user signup\nEmail: {user.email}",
            }

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

            logToSlack(slack_url, payload)

            return user


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6, trim_whitespace=True)
    email = serializers.EmailField(required=True, trim_whitespace=True)

    def validate_code(self, value):
        print(value)
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be a 6-digit number")

        return value

    def validate(self, data):
        with transaction.atomic():
            email = data["email"]
            submitted_hash = hash_code(data["code"])

            user = None

            # check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email.")

            otp = EmailOTP.objects.filter(
                user=user,
                code_hash=submitted_hash,
                expires_at__gt=timezone.now(),
                is_active=True,
            ).first()

            if not otp:
                raise serializers.ValidationError("Invalid or expired OTP.")

            data["user"] = user
            data["otp"] = otp
            return data

    def save(self):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]

        user.is_valid = True
        user.save(update_fields=["is_valid"])

        otp.is_active = False
        otp.save(update_fields=["is_active"])

        return user


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_valid:
            raise serializers.ValidationError("Email not verified")

        data["user"] = user

        return data


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name"]


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField()
    user = ProfileUserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user", "vibe_tag"]

    def validate_avatar(self, value):
        print(value)
        print(value.size)
        avatar_url = upload_to_cloudinary(value)

        if not avatar_url:
            raise serializers.ValidationError("File url does not exist")

        return avatar_url


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    token = serializers.UUIDField()

    def validate_password(self, value):
        return UserRegisterSerializer().validate_password(value)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user", "is_default"]


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        user = get_object_or_404(User, email=data["email"])

        if user.is_valid:
            raise serializers.ValidationError("Email has been verified")

        data["user"] = user

        return data
