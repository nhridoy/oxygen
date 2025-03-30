import contextlib

import pyotp
from cryptography.fernet import InvalidToken as FernetInvalidToken
from django.conf import settings
from django.contrib.auth import password_validation
from django.db.models import Q
from django.utils.translation import gettext as _
from jwt import ExpiredSignatureError
from rest_framework import serializers, validators

from authentications.models import User
from utils.helper import decode_token, decrypt


class PasswordValidateSerializer(serializers.Serializer):
    """
    Serializer for validating password
    """

    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )

    def validate_password(self, value):
        """
        Validate password
        """
        user = self.context["request"].user
        if user.check_password(value):
            return value
        raise serializers.ValidationError(_("Wrong Password"))


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )
    retype_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )

    def validate_old_password(self, value):
        """
        Validate old password
        """
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("You have entered Wrong password."))
        return value

    def validate_password(self, value):
        """
        Validate password
        """
        user = self.context["request"].user
        password_validation.validate_password(password=value, user=user)
        return value

    def validate_retype_password(self, value):
        """
        Validate retype password
        """
        if value != self.initial_data.get("password"):
            raise serializers.ValidationError(_("Passwords do not match"))
        return value


# ============***********============
# Password reset serializer
# ============***********============
class ResetPasswordSerializer(serializers.Serializer):
    """
    Reset Password Request Serializer
    """

    username = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def validate_username(self, value):
        try:
            self.user = User.objects.get(
                Q(email=value)
                | Q(username=value)
                | Q(user_information__phone_number=value)
            )
        except User.DoesNotExist as e:
            raise validators.ValidationError(
                detail=_(
                    "No active account found with the given email or username or phone number"
                )
            ) from e
        return value


class ResetPasswordCheckSerializer(serializers.Serializer):
    """
    Serializer for reset-password-check api view
    """

    secret = serializers.CharField(required=True)
    otp = serializers.CharField(required=False)

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload = None
        self.user = None
        self.verification_method = None

    def validate(self, attrs):
        if self.verification_method == "otp":
            return self.otp_validation(attrs.get("otp"))
        return attrs

    def validate_secret(self, value):
        try:
            self.payload = decode_token(decrypt(value))
            self.verification_method = self.payload.get("verification_method", "email")
            self.user: User = User.objects.get(id=self.payload.get("user"))
        except FernetInvalidToken as e:
            raise serializers.ValidationError(_("Invalid Secret")) from e
        except ExpiredSignatureError as e:
            raise serializers.ValidationError(_("Secret Expired")) from e
        return value

    def otp_validation(self, value):
        otp = pyotp.TOTP(
            self.payload.get("generated_key"),
            interval=settings.TOKEN_TIMEOUT_SECONDS,
        )
        if not value:
            raise serializers.ValidationError({"otp": _("OTP is required")})
        if not otp.verify(value):
            raise serializers.ValidationError({"otp": _("Invalid OTP")})
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """
    Reset Password Confirm Serializer
    """

    secret = serializers.CharField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        validators=[password_validation.validate_password],
    )
    retype_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload = None
        self.user = None

    def validate_secret(self, value):
        try:
            self.payload = decode_token(decrypt(value))
            if self.payload.get("reset_password") is not True:
                raise serializers.ValidationError(_("Invalid OTP Secret"))
        except FernetInvalidToken as e:
            raise serializers.ValidationError(_("Invalid OTP Secret")) from e
        except ExpiredSignatureError as e:
            raise serializers.ValidationError(_("OTP Secret Expired")) from e
        return value

    def validate_password(self, value):
        with contextlib.suppress(AttributeError):
            self.user: User = User.objects.get(id=self.payload.get("user"))
            password_validation.validate_password(password=value, user=self.user)
            return value

    def validate_retype_password(self, value):
        if value != self.initial_data.get("password"):
            raise serializers.ValidationError(_("Passwords do not match"))
        return value
