import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        dict_obj = {
            key.decode("utf-8"): value.decode("utf-8")
            for key, value in scope["headers"]
        }
        jwt_token = dict_obj.get("token")
        if jwt_token:
            try:
                decoded_token = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_id = decoded_token["user_id"]
                scope["user"] = await self.get_user(user_id)
            except jwt.ExpiredSignatureError:
                scope["user"] = AnonymousUser()
            except jwt.InvalidTokenError, KeyError:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
