from django.contrib import admin
from .models import UserDetail,UserInfo,UserLoginInfo
# Register your models here.

admin.site.register([UserDetail , UserInfo, UserLoginInfo])
