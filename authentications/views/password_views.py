from dj_rest_auth.jwt_auth import unset_jwt_cookies
from django.conf import settings
from django.contrib.auth import logout
from django.utils.translation import gettext as _
from rest_framework import decorators, response, status, viewsets

from authentications.serializers import (
    ChangePasswordSerializer,
    PasswordValidateSerializer,
)
from utils.extensions.permissions import IsAuthenticatedAndEmailVerified


class PasswordViewSet(viewsets.GenericViewSet):
    """
    Password view set
    """

    permission_classes = (IsAuthenticatedAndEmailVerified,)
    serializer_class = ChangePasswordSerializer
    queryset = None

    @decorators.action(
        detail=False, methods=["post"], serializer_class=PasswordValidateSerializer
    )
    def validate(self, request, *args, **kwargs):
        """
        Validate password
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return response.Response(
            {"detail": _("Password is valid")},
            status=status.HTTP_200_OK,
        )

    @decorators.action(
        detail=False, methods=["post"], serializer_class=ChangePasswordSerializer
    )
    def change(self, request, *args, **kwargs):
        """
        Change password
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        password = serializer.validated_data.get("password")

        return self._change_password(
            request=request,
            user=user,
            password=password,
        )

    @staticmethod
    def _logout_on_password_change(request, message):
        resp = response.Response(
            {"detail": message},
            status=status.HTTP_200_OK,
        )
        if settings.REST_AUTH.get("REST_SESSION_LOGIN"):
            logout(request)
        unset_jwt_cookies(resp)
        return resp

    def _change_password(self, request, user, password):
        user.set_password(password)
        user.save()
        message = _("Password updated successfully")
        if settings.REST_AUTH.get("LOGOUT_ON_PASSWORD_CHANGE"):
            self._logout_on_password_change(request=request, message=message)

        return response.Response(
            {"detail": message},
            status=status.HTTP_200_OK,
        )
