from django.urls import path
from api.views import (Login, Logout, CreateUser,GetUsers,UpdateUser,DeleteUser)

urlpatterns = [
    path('create_user', CreateUser.as_view(), name='create'),
    path('get_users', GetUsers.as_view(), name='get'),
    path('update_user_details/<str:username>', UpdateUser.as_view(), name='update'),
    path('delete_user/<str:username>', DeleteUser.as_view(), name='delete'),
    path('login', Login.as_view(), name='login'),
    path('logout/<str:username>', Logout.as_view(), name='logout'),
]
