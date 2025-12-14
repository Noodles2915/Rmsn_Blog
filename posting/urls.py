from django.urls import path
from . import views

app_name = 'posting'

urlpatterns = [
    path('new/', views.new_post, name='new_post'),
    path('search/', views.search_posts, name='search_posts'),
    path('<uuid:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<uuid:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<uuid:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<uuid:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<uuid:post_id>/', views.view_post, name='view_post'),
    path('tags/autocomplete/', views.tags_autocomplete, name='tags_autocomplete'),
]
