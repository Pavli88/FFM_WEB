from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

@database_sync_to_async
def get_user(validated_token):
    User = get_user_model()

    try:
        user_id = validated_token["user_id"]
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])

        # extract token from cookies
        raw_cookie = headers.get(b"cookie", b"").decode()
        cookies = {pair.split("=")[0]: pair.split("=")[1] for pair in raw_cookie.split("; ") if "=" in pair}

        access_token = cookies.get("access_token")  # vagy 'access_token' ha úgy nevezted el

        if access_token:
            try:
                validated_token = TokenBackend(
                    algorithm="HS256",
                    signing_key=settings.SECRET_KEY
                ).decode(access_token, verify=True)
                scope["user"] = await get_user(validated_token)
            except (InvalidToken, TokenError):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)