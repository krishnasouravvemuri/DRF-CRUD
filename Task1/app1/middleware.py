import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone

from app1.models import UserLoginInfo


class AuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):


        public_routes = [
                "/",             
                "/login",
                "/create-user",
                "/admin",
                "/static",
                "/media",
            ]

        if any(request.path.startswith(route) for route in public_routes):
            return self.get_response(request)

        # =========================
        # ✅ GET TOKEN
        # =========================
        token = request.headers.get("Authorization")

        if not token:
            return JsonResponse({"error": "Token missing"}, status=401)

        # =========================
        # ✅ VERIFY JWT
        # =========================
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # =========================
        # ✅ CHECK SESSION IN DB
        # =========================
        try:
            session = UserLoginInfo.objects.get(jwt_token=token,is_active=True)
        except UserLoginInfo.DoesNotExist:
            return JsonResponse({"error": "Session inactive"}, status=401)

        # =========================
        # ✅ CHECK EXPIRY (AUTO LOGOUT)
        # =========================
        if session.expires_at and session.expires_at < timezone.now():
            session.is_active = False
            session.save()

            return JsonResponse({"error": "Session expired. Please login again"}, status=401)

        # =========================
        # ✅ ATTACH USER
        # =========================
        request.user = session.user

        # continue to view
        return self.get_response(request)
