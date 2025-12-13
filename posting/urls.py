from django.urls import path
from . import views

app_name = 'posting'

urlpatterns = [
    path('new/', views.new_post, name='new_post'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<int:post_id>/', views.view_post, name='view_post'),
]
