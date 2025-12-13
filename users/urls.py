from django.urls import path
from . import views

# 指定 app_name 以便在包含时使用命名空间，例如 {% url 'users:login' %}
app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('send_vcode/', views.send_verification_code, name='send_vcode'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]