from django.db import models
import uuid
from django.utils import timezone


class UserInfo(models.Model):
    user_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,unique= True)
    user_name = models.CharField(max_length=20, unique= True)
    user_email = models.EmailField(unique= True)
    user_password = models.CharField(max_length=255)
    user_date_of_creation = models.DateField(auto_now_add=True)
    user_lat_passcode_update = models.DateField()
    user_active = models.PositiveSmallIntegerField()
    user_deleted = models.PositiveSmallIntegerField()
    user_role = models.PositiveSmallIntegerField()
    user_photo_path = models.CharField(max_length = 45)
    user_photo_link = models.CharField(max_length = 45)
    user_fullname = models.CharField(max_length = 45)

    def __str__(self):
        return self.user_name

class UserLoginInfo(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    login_session_id = models.CharField(max_length=64, unique=True)
    login_date_time = models.DateTimeField(auto_now_add = True)
    jwt_token = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.user_name} session"

class TeamInfo(models.Model):
    user = models.ForeignKey(UserInfo , on_delete = models.CASCADE , related_name = "Team_info")
    team_id = models.CharField(primary_key=True , max_length= 10)
    team_name = models.CharField(max_length = 15)
    team_created_by = models.CharField(max_length = 10)
    team_created_datetime = models.DateTimeField(auto_now_add=True)
    team_deleted = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"Team name is {self.team_name}"
    
class TeamUsers(models.Model):
    user = models.ForeignKey(UserInfo , on_delete = models.CASCADE , related_name = "username")
    team = models.ForeignKey(TeamInfo , on_delete = models.CASCADE , related_name = "Teamname")
    team_uer_team_role = models.PositiveSmallIntegerField()
    team_user_date_of_creation = models.DateTimeField(auto_now_add=True)
    team_user_active = models.PositiveSmallIntegerField()
    team_user_deleted = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"Team name is {self.team.team_name}"


class AllUserInfo_View(models.Model):

    # User
    user_id = models.UUIDField(primary_key=True)
    user_name = models.CharField(max_length=20)
    user_email = models.EmailField()
    user_password = models.CharField(max_length=255)
    user_date_of_creation = models.DateField()
    user_lat_passcode_update = models.DateField()
    user_active = models.PositiveSmallIntegerField()
    user_deleted = models.PositiveSmallIntegerField()
    user_role = models.PositiveSmallIntegerField()
    user_photo_path = models.CharField(max_length=45)
    user_photo_link = models.CharField(max_length=45)
    user_fullname = models.CharField(max_length=45)

    # Login
    login_session_id = models.CharField(max_length=64, null=True)
    login_date_time = models.DateTimeField(null=True)
    jwt_token = models.TextField(null=True)
    login_is_active = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)

    # Team
    team_id = models.CharField(max_length=10, null=True)
    team_name = models.CharField(max_length=15, null=True)
    team_created_by = models.CharField(max_length=10, null=True)
    team_created_datetime = models.DateTimeField(null=True)
    team_deleted = models.PositiveSmallIntegerField(null=True)

    # TeamUsers
    team_uer_team_role = models.PositiveSmallIntegerField(null=True)
    team_user_date_of_creation = models.DateTimeField(null=True)
    team_user_active = models.PositiveSmallIntegerField(null=True)
    team_user_deleted = models.PositiveSmallIntegerField(null=True)

    class Meta:
        managed = False
        db_table = "AllUserInfo_View"