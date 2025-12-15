"""
URL configuration for RmsnBlog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 将 users 应用包含为命名空间，确保模板中使用 'users:...' 可被解析
    path('user/', include(('users.urls', 'users'), namespace='users')),
    path('post/', include(('posting.urls', 'posting'), namespace='posting')),
    path('socials/', include(('socials.urls', 'socials'), namespace='socials')),
    path('', views.index, name='index'),
]

# 开发环境下提供媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

