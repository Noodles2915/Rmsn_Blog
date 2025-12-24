from django.shortcuts import render, redirect
from users.views import get_current_user
from posting.models import Post
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.urls import reverse
from django.core.paginator import Paginator


def index(request):
    user = get_current_user(request)

    # 获取最新3篇文章并在视图中预处理展示所需的字段
    qs = Post.objects.all().select_related('author').prefetch_related('tags').order_by('-created_at')[:3]
    posts = []
    for p in qs:
        import re
        # 移除代码块（<pre> 和 <code>）
        content_no_code = re.sub(r'<pre[^>]*>.*?</pre>', ' ', p.content, flags=re.DOTALL)
        content_no_code = re.sub(r'<code[^>]*>.*?</code>', ' ', content_no_code, flags=re.DOTALL)
        # 去掉剩余HTML标签并清理多余空白
        clean_content = strip_tags(content_no_code)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        excerpt = Truncator(clean_content).chars(200)
        author_display = p.author.username
        # 获取标签列表
        tags = [{'name': tag.name, 'url': reverse('posting:search_posts') + f'?q=%23{tag.name}'} for tag in p.tags.all()]
        posts.append({
            'title': p.title,
            'url': reverse('posting:view_post', args=[p.id]),
            'author': author_display,
            'author_username': p.author.username,
            'author_avatar': p.author.avatar_url,
            'created_at': p.created_at,
            'excerpt': excerpt,
            'tags': tags,
        })

    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'index.html', context)


def all_posts(request):
    """显示所有博客，分页，每页5条，按时间倒序"""
    user = get_current_user(request)
    
    # 获取所有文章，按时间倒序
    qs = Post.objects.all().select_related('author').prefetch_related('tags').order_by('-created_at')
    
    # 分页，每页5条
    paginator = Paginator(qs, 5)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    
    # 预处理数据
    posts = []
    for p in page_obj:
        import re
        # 移除代码块（<pre> 和 <code>）
        content_no_code = re.sub(r'<pre[^>]*>.*?</pre>', ' ', p.content, flags=re.DOTALL)
        content_no_code = re.sub(r'<code[^>]*>.*?</code>', ' ', content_no_code, flags=re.DOTALL)
        # 去掉剩余HTML标签并清理多余空白
        clean_content = strip_tags(content_no_code)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        excerpt = Truncator(clean_content).chars(200)
        # 获取标签列表
        tags = [{'name': tag.name, 'url': reverse('posting:search_posts') + f'?q=%23{tag.name}'} for tag in p.tags.all()]
        posts.append({
            'title': p.title,
            'url': reverse('posting:view_post', args=[p.id]),
            'author': p.author.username,
            'author_username': p.author.username,
            'author_avatar': p.author.avatar_url,
            'created_at': p.created_at,
            'excerpt': excerpt,
            'tags': tags,
        })
    
    context = {
        'user': user,
        'posts': posts,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'all_posts.html', context)
