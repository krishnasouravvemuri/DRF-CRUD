from django.db import models
import uuid
from django.utils import timezone


class UserInfo(models.Model):
    user_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user_email = models.EmailField()
    username = models.CharField(max_length=20, unique= True)
    password = models.CharField(max_length=255)
    def __str__(self):
        return self.username


class UserDetail(models.Model):
    user = models.ForeignKey(UserInfo,on_delete=models.CASCADE,related_name='details')
    user_age = models.IntegerField()
    user_contact_no = models.CharField(max_length=10, unique=True)
    user_address = models.CharField(max_length=100)
    user_current_company = models.CharField(max_length=50)
    user_yoe = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.username} details"


class UserLoginInfo(models.Model):

    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=64, unique=True)
    jwt_token = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} session"
