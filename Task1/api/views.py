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


class CreateUser(APIView):

    def post(self, request):

        data = request.data.copy()
        password = data.get("password")

        if password:
            hashed = bcrypt.hashpw(
                password.encode(),
                bcrypt.gensalt()
            ).decode()

            data["password"] = hashed

        serializer = UserInfoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse(None, status.HTTP_201_CREATED, "User created successfully").build()

        return ApiResponse(serializer.errors, status.HTTP_400_BAD_REQUEST, "Validation error").build()


class UserDetails(APIView):

    def get_object(self, username):
        try:
            return UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            return None

    def get(self, request, username):
        user = self.get_object(username)

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user)
        return ApiResponse(serializer.data, 200, "User retrieved successfully").build()

    def post(self, request, username):
        user = self.get_object(username)

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return ApiResponse(serializer.data, 201, "User details added successfully").build()

        return ApiResponse(serializer.errors, 400, "Validation error").build()


class GetUsers(APIView):

    def get(self, request):
        users = UserInfo.objects.all()
        serializer = UserInfoSerializer(users, many=True)

        return ApiResponse(serializer.data, 200, "Users fetched successfully").build()


class UpdateUser(APIView):

    def get_object(self, username):
        try:
            return UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            return None

    def get(self, request, username):
        user = self.get_object(username)

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user)
        return ApiResponse(serializer.data, 200, "User retrieved successfully").build()

    def patch(self, request, username):
        user = self.get_object(username)

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse(serializer.data, 200, "User updated successfully").build()

        return ApiResponse(serializer.errors, 400, "Validation error").build()


class DeleteUser(APIView):

    def get_object(self, username):
        try:
            return UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            return None

    def get(self, request, username):
        user = self.get_object(username)

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        serializer = UserInfoSerializer(user)
        return ApiResponse(serializer.data, 200, "User retrieved successfully").build()

    def delete(self, request, username):
        user = self.get_object(username)

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        user.delete()
        return ApiResponse(None, 200, "User deleted successfully").build()


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

        session_key = secrets.token_hex(32)
        expiry_time = timezone.now() + timedelta(hours=settings.TOKEN_EXPIRY_HOURS)
        payload = {
            "username": user.username,
            "exp" : expiry_time
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        UserLoginInfo.objects.create(
            user=user,
            session_key=session_key,
            jwt_token=token,
            expires_at=expiry_time
        )

        return ApiResponse({"token": token}, 200, "Login successful").build()


class Logout(APIView):

    def logout_user(self, request, username):
        token = request.headers.get("Authorization")

        if not token:
            return ApiResponse(None, 401, "Unauthorized").build()

        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"],options={"verify_exp": False})
        except jwt.InvalidTokenError:
            return ApiResponse(None, 401, "Invalid token").build()

        if payload.get("username") != username:
            return ApiResponse(None, 403, "Token mismatch").build()

        try:
            session = UserLoginInfo.objects.get(jwt_token=token,is_active=True,user__username=username)
        except UserLoginInfo.DoesNotExist:
            return ApiResponse(None, 401, "Already logged out or expired").build()

        session.is_active = False
        session.save()

        return ApiResponse(None, 200, "Logged out successfully").build()

    def post(self, request, username):
        return self.logout_user(request, username)

    def get(self, request, username):
        return self.logout_user(request, username)
