from django.contrib import admin
from .models import Follow, Notification, Message


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    search_fields = ('follower__username', 'followed__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'verb', 'unread', 'created_at')
    list_filter = ('unread',)
    search_fields = ('user__username', 'actor__username', 'verb')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'created_at', 'is_read')
    search_fields = ('sender__username', 'recipient__username', 'content')
from django.contrib import admin

# Register your models here.
