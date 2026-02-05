from rest_framework import serializers
from app1.models import  UserInfo , TeamInfo , TeamUsers


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "__all__"

class TeamInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInfo
        fields = "__all__"

class TeamUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamUsers
        fields = "__all__"