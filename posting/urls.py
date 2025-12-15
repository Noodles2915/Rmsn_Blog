from django.urls import path
from . import views

app_name = 'posting'

urlpatterns = [
    path('new/', views.new_post, name='new_post'),
    # 前后端解耦API
    path('api/<uuid:post_id>/', views.api_post_detail, name='api_post_detail'),
    path('api/<uuid:post_id>/comments/', views.api_post_comments, name='api_post_comments'),
    path('api/<uuid:post_id>/comment/', views.api_add_comment_api, name='api_add_comment_api'),
    path('search/', views.search_posts, name='search_posts'),
    path('<uuid:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<uuid:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<uuid:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<uuid:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('comment/<uuid:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<uuid:post_id>/', views.view_post, name='view_post'),
    path('tags/autocomplete/', views.tags_autocomplete, name='tags_autocomplete'),
]
