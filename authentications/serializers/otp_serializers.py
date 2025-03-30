from django.conf import settings
from django.utils.translation import gettext as _
from pyotp import TOTP
from rest_framework import serializers

from authentications.models import UserTwoStepVerification
from utils.helper import encrypt


class OTPCreateSerializer(serializers.Serializer):
    """
    Serializer for QR create view
    """

    generated_key = serializers.CharField()
    otp = serializers.CharField(write_only=True)
    otp_method = serializers.ChoiceField(
        choices=["authenticator_app", "email", "sms"],
        write_only=True,
        default="authenticator_app",
    )

    def validate_otp(self, value):
        request = self.context.get("request")
        generated_key = self.initial_data.get("generated_key")
        otp_method = self.initial_data.get("otp_method", "authenticator_app")
        user = request.user
        if otp_method == "authenticator_app":
            otp = TOTP(generated_key)
            if not otp.verify(value):
                raise serializers.ValidationError(_("Invalid OTP"))
        else:
            otp = TOTP(
                generated_key,
                interval=settings.TOKEN_TIMEOUT_SECONDS,
            )
            if not otp.verify(value):
                raise serializers.ValidationError(_("Invalid OTP"))
        user_otp = UserTwoStepVerification.objects.get(user=user)
        user_otp.secret_key = encrypt(generated_key)
        user_otp.otp_method = otp_method
        user_otp.is_active = True
        user_otp.save(update_fields=["secret_key", "otp_method", "is_active"])
        return value
