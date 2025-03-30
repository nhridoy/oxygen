from django.utils.translation import gettext as _
from rest_framework import decorators, viewsets
from rest_framework.response import Response

from authentications import serializers
from authentications.serializers import (
    ResetPasswordCheckSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordSerializer,
)
from authentications.views.common_functions import (
    generate_and_send_otp,
    generate_link,
    generate_token,
    get_origin,
    send_verification_email,
)


class ResetPasswordViewSet(viewsets.GenericViewSet):
    """
    View for getting email or sms for password reset
    post: email: ""
    """

    serializer_class = serializers.ResetPasswordSerializer
    authentication_classes = []
    permission_classes = []

    # throttle_classes = (AnonUserRateThrottle,)

    @staticmethod
    def email_sender_helper(user, origin):
        url = generate_link(user, origin, "reset-password")
        send_verification_email(user, url)

        return Response({"data": {"detail": _("Verification Email Sent")}})

    @decorators.action(
        detail=False,
        methods=["post"],
        serializer_class=ResetPasswordSerializer,
        url_path="email",
    )
    def send_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        return self.email_sender_helper(user, get_origin(self.request))

    @decorators.action(
        detail=False,
        methods=["post"],
        serializer_class=ResetPasswordSerializer,
        url_path="sms",
    )
    def send_sms(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        return generate_and_send_otp(user, "sms", True, verification_method="otp")

    @decorators.action(
        detail=False,
        methods=["post"],
        serializer_class=ResetPasswordSerializer,
        url_path="email-otp",
    )
    def send_otp_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        return generate_and_send_otp(user, "email", True, verification_method="otp")

    @decorators.action(
        detail=False,
        methods=["post"],
        serializer_class=ResetPasswordCheckSerializer,
        url_path="check",
    )
    def check(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "data": {
                    "detail": "Accepted",
                    "secret": generate_token(
                        serializer.user,
                        reset_password=True,
                        verification_method=serializer.verification_method,
                    ),
                }
            }
        )

    @decorators.action(
        detail=False,
        methods=["post"],
        serializer_class=ResetPasswordConfirmSerializer,
        url_path="confirm",
    )
    def confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self._change_password(serializer)

    @staticmethod
    def _change_password(serializer):
        user = serializer.user
        user.set_password(serializer.validated_data.get("password"))
        user.save(update_fields=["password"])
        return Response({"detail": _("Password Changed Successfully")})
