from django.shortcuts import render, redirect
from users.views import get_current_user
from posting.models import Post
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.urls import reverse


def index(request):
    user = get_current_user(request)

    # 获取最新文章并在视图中预处理展示所需的简单字段，减少模板逻辑和数据库访问
    qs = Post.objects.all().select_related('author').prefetch_related('tags').order_by('-created_at')[:10]
    posts = []
    for p in qs:
        excerpt = Truncator(strip_tags(p.content)).chars(140)
        author_display = p.author.username
        posts.append({
            'title': p.title,
            'url': reverse('posting:view_post', args=[p.id]),
            'author': author_display,
            'author_username': p.author.username,
            'created_at': p.created_at,
            'excerpt': excerpt,
        })

    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'index.html', context)
