from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import exceptions
from rest_framework import request as drf_request

UserModel = get_user_model()


class EmailAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return

        try:
            user = UserModel.objects.get(
                Q(email=username)
                | Q(username=username)
                | Q(user_information__phone_number=username)
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
            raise exceptions.AuthenticationFailed(
                _("No active account found with the given credentials")
            )

        if not self.user_can_authenticate(user):
            raise exceptions.AuthenticationFailed(_("User is deactivated"))

        max_login_attempts = settings.MAX_LOGIN_ATTEMPTS
        blocked_minutes = settings.BLOCKED_MINUTES

        if user.check_password(password):
            if user.blocked_until and user.blocked_until > timezone.now():
                self._raise_blocked_error(request, max_login_attempts, blocked_minutes)
            # if user.blocked_until and user.blocked_until < timezone.now():
            user.failed_login_attempts = 0
            user.blocked_until = None
            user.save()
            return user

        if max_login_attempts > 0 and blocked_minutes > 0:
            if user.blocked_until and user.blocked_until > timezone.now():
                self._raise_blocked_error(request, max_login_attempts, blocked_minutes)
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= max_login_attempts:
                user.failed_login_attempts = 0
                user.blocked_until = timezone.now() + timedelta(minutes=blocked_minutes)
            user.save()

    @staticmethod
    def _raise_blocked_error(request, max_login_attempts, blocked_minutes):
        error_message = _(
            "You have exceeded the maximum number of login attempts ({max_login_attempts} times). Please try again after {blocked_minutes} minutes"
        ).format(max_login_attempts=max_login_attempts, blocked_minutes=blocked_minutes)

        if isinstance(request, drf_request.Request):
            raise exceptions.AuthenticationFailed(error_message)
        raise ValidationError(error_message)
