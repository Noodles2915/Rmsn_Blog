from django.urls import path
from . import views

app_name = 'socials'

urlpatterns = [
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/count/', views.notifications_count, name='notifications_count'),
    path('messages/count/', views.messages_count, name='messages_count'),
    path('notifications/mark_read/', views.mark_notification_read, name='notifications_mark_read'),
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/send/<str:username>/', views.send_message, name='send_message'),
]
