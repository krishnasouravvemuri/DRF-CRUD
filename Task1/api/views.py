import bcrypt
import secrets
import jwt

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from app1.models import (UserInfo,UserLoginInfo,TeamInfo,AllUserInfo_View)
from api.serializers import UserInfoSerializer



class ApiResponse:
    def __init__(self, response_data=None, status_code=200, message=""):
        self.response_data = response_data
        self.status_code = status_code
        self.message = message

    def build(self):
        return Response(
            {"meta": 
               {"code": self.status_code,
                "message": self.message},
                "data": self.response_data},
                status=self.status_code
            )

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
    data.pop("user_password", None)
    return data


class CreateUser(APIView):

    def post(self, request):
        data = request.data.copy()

        password = data.get("user_password")

        if password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            data["user_password"] = hashed

        serializer = UserInfoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse(None, 201, "User created successfully").build()

        return ApiResponse(serializer.errors, 400, "Validation error").build()


class GetUsers(APIView):

    def get(self, request):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        users = UserInfo.objects.filter(user_deleted=0)
        serializer = UserInfoSerializer(users, many=True)

        cleaned = [remove_password(u) for u in serializer.data]

        return ApiResponse(cleaned, 200, "Users fetched successfully").build()

class UpdateUser(APIView):

    def get_object(self, username):
        return UserInfo.objects.filter(user_name=username).first()

    def patch(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = self.get_object(username)

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        data = request.data.copy()

        if "user_password" in data:
            data["user_password"] = bcrypt.hashpw(
                data["user_password"].encode(),
                bcrypt.gensalt()
            ).decode()

        serializer = UserInfoSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse(remove_password(serializer.data), 200, "User updated").build()

        return ApiResponse(serializer.errors, 400, "Validation error").build()


class DeleteUser(APIView):

    def delete(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        user = UserInfo.objects.filter(user_name=username).first()

        if not user:
            return ApiResponse(None, 404, "User not found").build()

        user.user_deleted = 1
        user.save()

        return ApiResponse(None, 200, "User deleted successfully").build()


class Login(APIView):

    def post(self, request):

        username = request.data.get("user_name")
        password = request.data.get("user_password")

        user = UserInfo.objects.filter(user_name=username).first()

        if not user:
            return ApiResponse(None, 401, "Invalid user").build()

        if not bcrypt.checkpw(password.encode(), user.user_password.encode()):
            return ApiResponse(None, 401, "Wrong password").build()

        expiry = timezone.now() + timedelta(hours=settings.TOKEN_EXPIRY_HOURS)

        payload = {
            "user_name": user.user_name,
            "exp": expiry
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        UserLoginInfo.objects.create(
            user=user,
            login_session_id=secrets.token_hex(32),
            jwt_token=token,
            expires_at=expiry
        )

        return ApiResponse({"token": token}, 200, "Login successful").build()


class Logout(APIView):

    def post(self, request, username):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        token = request.headers.get("Authorization")

        session = UserLoginInfo.objects.filter(
            jwt_token=token,
            user__user_name=username,
            is_active=True
        ).first()

        if not session:
            return ApiResponse(None, 401, "Already logged out").build()

        session.is_active = False
        session.save()

        return ApiResponse(None, 200, "Logged out successfully").build()


class UserInfoView(APIView):

    def get(self, request):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        data = list(
            AllUserInfo_View.objects.all().values()
        )

        for d in data:
            d.pop("user_password", None)

        return ApiResponse(data, 200, "User info view fetched").build()


class TeamInfoView(APIView):

    def get(self, request):
        ok, resp = verify_token(request)
        if not ok:
            return resp

        teams = TeamInfo.objects.filter(team_deleted=0).values()

        return ApiResponse(list(teams), 200, "Teams fetched").build()