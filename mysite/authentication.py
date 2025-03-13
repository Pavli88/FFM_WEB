from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Először próbáljuk az Authorization fejlécet használni
        header_auth = super().authenticate(request)

        if header_auth:
            return header_auth

        # Ha nincs Authorization fejléc, nézzük meg a sütiket
        access_token = request.COOKIES.get("access_token")

        if access_token:
            validated_token = self.get_validated_token(access_token)

            return self.get_user(validated_token), validated_token
        return None
