import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone

from app1.models import UserLoginInfo


class AuthMiddleware:
    """
    Protects ONLY secured API routes

    Public:
        /
        /admin/*
        /api/login
        /api/create_user

    Protected:
        everything else under /api/*
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        path = request.path

        # =========================
        # ✅ PUBLIC ROUTES
        # =========================
        public_routes = [
            "/",                      # homepage
            "/admin",                 # admin panel
            "/api/login",
            "/api/create_user",
        ]

        # allow public routes
        if any(path.startswith(route) for route in public_routes):
            return self.get_response(request)

        # =========================
        # ✅ ONLY PROTECT /api/*
        # =========================
        if not path.startswith("/api/"):
            return self.get_response(request)

        # =========================
        # 🔐 TOKEN REQUIRED BELOW
        # =========================
        token = request.headers.get("Authorization")

        if not token:
            return JsonResponse({"error": "Token missing"}, status=401)

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        # verify jwt
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # check loginInfo
        try:
            loginInfo = UserLoginInfo.objects.get(jwt_token=token,is_active=True)
        except UserLoginInfo.DoesNotExist:
            return JsonResponse({"error": "Session inactive"}, status=401)

        # expiry check
        if loginInfo.expires_at and loginInfo.expires_at < timezone.now():
            loginInfo.is_active = False
            loginInfo.save()
            return JsonResponse({"error": "loginInfo expired"}, status=401)

        request.user = loginInfo.user

        return self.get_response(request)