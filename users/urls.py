from django.urls import path
from . import views

# 指定 app_name 以便在包含时使用命名空间，例如 {% url 'users:login' %}
app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]