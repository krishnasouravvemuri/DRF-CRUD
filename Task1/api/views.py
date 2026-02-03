import bcrypt
import secrets
import jwt

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from app1.models import UserInfo, UserDetail, UserLoginInfo
from api.serializers import UserInfoSerializer, UserDetailSerializer


# =====================================
# Common API Response
# =====================================
class ApiResponse:
    def __init__(self, response_data=None, status_code=200, message=""):
        self.response_data = response_data
        self.status_code = status_code
        self.message = message

    def build(self):
        return Response(
            {
                "meta": {
                    "code": self.status_code,
                    "message": self.message
                },
                "data": self.response_data
            },
            status=self.status_code
        )


# =====================================
# 🔐 HELPER (just a small function)
# =====================================
def verify_token(request):
    token = request.headers.get("Authorization")

    if not token:
        return False, ApiResponse(None, 401, "Authorization token required").build()

    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return False, ApiResponse(None, 401, "Token expired").build()
    except jwt.InvalidTokenError:
        return False, ApiResponse(None, 401, "Invalid token").build()

    return True, None


def remove_password(data):
    data.pop("password", None)
    return data


# =====================================
# CREATE USER (NO AUTH)
# =====================================
class CreateUser(APIView):

    def post(self, request):

        data = request.data.copy()
        password = data.get("password")

        if password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            data["password"] = hashed

        serializer = UserInfoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse(None, 201, "User created successfully").build()

        return ApiResponse(serializer.errors, 400, "Validation error").build()


# =====================================
# USER DETAILS (AUTH REQUIRED)
# =====================================
class UserDetails(APIView):

    def get_object(self, username):
        try:
            return UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            return None

    def get(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = self.get_object(username)
        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user)
        return ApiResponse(remove_password(serializer.data), 200, "User retrieved successfully").build()

    def post(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = self.get_object(username)
        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return ApiResponse(serializer.data, 201, "User details added successfully").build()

        return ApiResponse(serializer.errors, 400, "Validation error").build()


# =====================================
# GET USERS (AUTH REQUIRED)
# =====================================
class GetUsers(APIView):

    def get(self, request):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        users = UserInfo.objects.all()
        serializer = UserInfoSerializer(users, many=True)

        cleaned = [remove_password(u) for u in serializer.data]

        return ApiResponse(cleaned, 200, "Users fetched successfully").build()


# =====================================
# UPDATE USER (AUTH REQUIRED)
# =====================================
class UpdateUser(APIView):

    def get_object(self, username):
        try:
            return UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            return None

    def get(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = self.get_object(username)
        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user)
        return ApiResponse(remove_password(serializer.data), 200, "User retrieved successfully").build()

    def patch(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = self.get_object(username)
        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse(remove_password(serializer.data), 200, "User updated successfully").build()

        return ApiResponse(serializer.errors, 400, "Validation error").build()


# =====================================
# DELETE USER (AUTH REQUIRED)
# =====================================
class DeleteUser(APIView):

    def get_object(self, username):
        try:
            return UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            return None

    def get(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = self.get_object(username)
        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user)
        return ApiResponse(remove_password(serializer.data), 200, "User retrieved successfully").build()

    def delete(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = self.get_object(username)
        if not user:
            return ApiResponse(None, 404, "User not found").build()

        user.delete()
        return ApiResponse(None, 200, "User deleted successfully").build()


# =====================================
# LOGIN (NO AUTH)
# =====================================
class Login(APIView):

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            return ApiResponse(None, 401, "Invalid user").build()

        if not bcrypt.checkpw(password.encode(), user.password.encode()):
            return ApiResponse(None, 401, "Wrong password").build()

        expiry_time = timezone.now() + timedelta(hours=settings.TOKEN_EXPIRY_HOURS)

        payload = {
            "username": user.username,
            "exp": expiry_time
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        UserLoginInfo.objects.create(
            user=user,
            session_key=secrets.token_hex(32),
            jwt_token=token,
            expires_at=expiry_time
        )

        return ApiResponse({"token": token}, 200, "Login successful").build()


# =====================================
# LOGOUT (AUTH REQUIRED)
# =====================================
class Logout(APIView):

    def post(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        token = request.headers.get("Authorization")

        session = UserLoginInfo.objects.filter(
            jwt_token=token,
            user__username=username,
            is_active=True
        ).first()

        if not session:
            return ApiResponse(None, 401, "Already logged out or expired").build()

        session.is_active = False
        session.save()

        return ApiResponse(None, 200, "Logged out successfully").build()
