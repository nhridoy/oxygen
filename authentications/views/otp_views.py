import pyotp
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, password_validation  # noqa
from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import (  # noqa
    decorators,
    exceptions,
    generics,
    permissions,
    response,
    status,
    views,
    viewsets,
)

from authentications.models import User, UserTwoStepVerification
from authentications.serializers import OTPCreateSerializer
from utils.extensions import validate_query_params

from .common_functions import (
    generate_and_send_otp,
)


class OTPView(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OTPCreateSerializer
    queryset = UserTwoStepVerification.objects.all()

    @staticmethod
    def _clear_user_otp(user_otp):
        user_otp.secret_key = ""
        user_otp.otp_method = "___"
        user_otp.is_active = False
        user_otp.save(update_fields=["secret_key", "otp_method", "is_active"])

    @decorators.action(
        detail=False,
        methods=["get"],
    )
    def check(self, request, *args, **kwargs):
        user_otp = request.user.user_two_step_verification.is_active
        return response.Response(
            {"is_active": user_otp},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "otp_method",
                type={"type": "string"},
                enum=["authenticator_app", "email", "sms"],
                default="authenticator_app",
                style="form",
                explode=False,
                required=True,
            )
        ]
    )
    @validate_query_params("otp_method", ["authenticator_app", "email", "sms"])
    @decorators.action(
        detail=False,
        methods=["get"],
    )
    def generate(self, request, *args, **kwargs):
        current_user: User = request.user
        if (
            otp_method := request.query_params.get("otp_method", "authenticator_app")
        ) == "authenticator_app":
            generated_key = pyotp.random_base32()
            qr_key = pyotp.TOTP(generated_key).provisioning_uri(
                name=current_user.email, issuer_name=settings.PROJECT_NAME
            )
            return response.Response(
                {
                    "data": {
                        "qr_key": qr_key,
                        "generated_key": generated_key,
                        "otp_method": otp_method,
                    },
                    "message": _("QR Code is generated"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return generate_and_send_otp(current_user, otp_method)

    @decorators.action(
        detail=False,
        methods=["post"],
    )
    def validate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return response.Response(
            {
                "data": {"detail": _("OTP is activated")},
                "message": _("OTP is activated"),
            },
            status=status.HTTP_200_OK,
        )

    @decorators.action(
        detail=False,
        methods=["delete"],
    )
    def delete(self, request, *args, **kwargs):
        current_user = self.request.user
        user_otp = generics.get_object_or_404(
            UserTwoStepVerification, user=current_user
        )
        self._clear_user_otp(user_otp)
        return response.Response({"message": _("OTP Removed")})
