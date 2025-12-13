from django.shortcuts import render, redirect
from users.views import get_current_user
from posting.models import Post

def index(request):
    user = get_current_user(request)
    
    # 获取最新发布的文章
    posts = Post.objects.all().order_by('-created_at')[:10]
    
    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'index.html', context)
