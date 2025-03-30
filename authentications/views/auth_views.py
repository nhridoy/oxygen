import contextlib
from typing import Any

from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from fcm_django.models import FCMDevice
from rest_framework import exceptions, generics, permissions, response, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from authentications.models import User
from authentications.serializers import (
    FCMDeleteSerializer,
    LoginSerializer,
    OTPLoginSerializer,
)

from .common_functions import (
    direct_login,
    extract_token,
    generate_and_send_otp,
    generate_token,
    get_token,
    set_jwt_access_cookie,
    set_jwt_refresh_cookie,
    unset_jwt_cookies,
)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    @staticmethod
    def _authenticator_login(user):
        """
        Method for returning secret key if OTP is active for user
        """
        secret = generate_token(user)
        return Response(
            {"secret": secret},
            status=status.HTTP_202_ACCEPTED,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User = serializer.validated_data[1]
        if settings.REQUIRED_EMAIL_VERIFICATION and not user.is_verified:
            raise exceptions.PermissionDenied("Email not Verified")

        if user.user_two_step_verification.is_active:
            otp_method: Any = user.user_two_step_verification.otp_method
            if otp_method == "authenticator_app":
                return self._authenticator_login(user)
            else:
                return generate_and_send_otp(user, otp_method, True)
        else:
            return direct_login(request, Response(), user, serializer.validated_data[0])


class MyTokenRefreshView(generics.GenericAPIView):
    """
    View for get new access token for a valid refresh token
    """

    serializer_class = TokenRefreshSerializer
    permission_classes = ()
    authentication_classes = ()

    @staticmethod
    def _set_cookie(resp, serializer, domain):
        if refresh := serializer.validated_data.get(
            settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
        ):  # noqa
            set_jwt_refresh_cookie(
                resp=resp,
                refresh_token=refresh,
                domain=domain,
            )
        set_jwt_access_cookie(
            resp=resp,
            access_token=serializer.validated_data.get(
                settings.REST_AUTH.get("JWT_AUTH_COOKIE")
            ),  # noqa
            domain=domain,
        )

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(
            settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
        ) or request.data.get(settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE"))

        serializer = self.serializer_class(
            data={settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE"): refresh}
        )
        serializer.is_valid(raise_exception=True)
        resp = Response()

        # try:
        #     domain = get_origin(self.request).split("//")[1].split(":")[0]
        # except Exception as e:
        #     domain = None
        self._set_cookie(resp=resp, serializer=serializer, domain=None)
        resp.data = serializer.validated_data
        resp.status_code = status.HTTP_200_OK
        return resp


class LogoutView(views.APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """

    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = "dj_rest_auth"

    def get(self, request, *args, **kwargs):
        if getattr(settings, "ACCOUNT_LOGOUT_ON_GET", False):
            resp = self._logout(request)
        else:
            resp = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, resp, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._logout(request)

    @staticmethod
    def _logout(request):
        with contextlib.suppress(AttributeError, ObjectDoesNotExist):
            request.user.auth_token.delete()

        if settings.REST_AUTH.get("SESSION_LOGIN", False):
            logout(request)

        resp = Response(
            {"detail": _("Successfully logged out.")},
            status=status.HTTP_200_OK,
        )

        if settings.REST_AUTH.get("USE_JWT", True):
            cookie_name = settings.REST_AUTH.get("JWT_AUTH_COOKIE", "access")

            # try:
            #     domain = get_origin(request).split("//")[1].split(":")[0]
            # except Exception as e:
            #     domain = None

            unset_jwt_cookies(resp, None)

            if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
                # add refresh token to blacklist
                try:
                    token = RefreshToken(
                        request.COOKIES.get(
                            settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
                        )
                        or request.data.get(
                            settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
                        )
                    )
                    token.blacklist()
                except KeyError:
                    resp.data = {
                        "detail": _("Refresh token was not included in request data.")
                    }
                    resp.status_code = status.HTTP_401_UNAUTHORIZED
                except (TokenError, AttributeError, TypeError) as error:
                    if hasattr(error, "args"):
                        if (
                            "Token is blacklisted" in error.args
                            or "Token is invalid or expired" in error.args
                        ):
                            resp.data = {"detail": error.args[0]}
                            resp.status_code = status.HTTP_401_UNAUTHORIZED
                        else:
                            resp.data = {"detail": _("An error has occurred.")}
                            resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

                    else:
                        resp.data = {"detail": _("An error has occurred.")}
                        resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            elif not cookie_name:
                message = _(
                    "Neither cookies or blacklist are enabled, so the token "
                    "has not been deleted server side. "
                    "Please make sure the token is deleted client side.",
                )
                resp.data = {"detail": message}
                resp.status_code = status.HTTP_200_OK
        return resp


class OTPLoginView(generics.GenericAPIView):
    serializer_class = OTPLoginSerializer
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        token = extract_token(get_token(user))
        return direct_login(request, Response(), user, token)


class FCMDeleteView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FCMDeleteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        device = generics.get_object_or_404(
            FCMDevice,
            user=self.request.user,
            registration_id=serializer.validated_data.get("device_id"),
        )

        device.delete()

        return response.Response({"data": "Deleted Successfully"})
