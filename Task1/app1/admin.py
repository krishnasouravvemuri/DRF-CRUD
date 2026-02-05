from django.contrib import admin
from .models import UserInfo,UserLoginInfo , TeamInfo , TeamUsers
# Register your models here.

admin.site.register([ UserInfo, UserLoginInfo , TeamUsers , TeamInfo])
