from functools import wraps

from django.utils.translation import gettext as _
from rest_framework import exceptions


def validate_query_params(query_name, valid_params):
    def decorator(func):
        @wraps(func)
        def wrapped(self, request, *args, **kwargs):
            query_params = request.query_params.get(query_name, None)

            if not query_params:
                raise exceptions.ValidationError(
                    _(
                        f"No query parameters provided. Options are: {query_name}={valid_params or ''}"
                    )
                )

            if valid_params and query_params not in valid_params:
                raise exceptions.ValidationError(
                    _(
                        f"Invalid query parameter: {query_params}. Options are: {query_name}={valid_params}"
                    )
                )

            return func(self, request, *args, **kwargs)

        return wrapped

    return decorator
