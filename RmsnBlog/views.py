from django.shortcuts import render, redirect
from users.views import get_current_user
from posting.models import Post
from markdownx.utils import markdownify
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
        # 优先使用已渲染的 HTML（p.content），若为空或看起来不是 HTML，则回退渲染可用的原始 Markdown（content_raw 或 p.content）
        content_source = p.content or ''
        if not content_source or '<' not in content_source:
            raw_fallback = getattr(p, 'content_raw', '') or p.content or ''
            if raw_fallback:
                content_source = markdownify(raw_fallback)
            else:
                content_source = p.content or ''

        # 额外清理：移除 Markdown 围栏代码（```...``` 或 ~~~...~~~），然后移除 HTML 的 <pre>/<code>
        content_source = re.sub(r'```.*?```', ' ', content_source, flags=re.DOTALL)
        content_source = re.sub(r'~~~.*?~~~', ' ', content_source, flags=re.DOTALL)
        content_no_code = re.sub(r'<pre[^>]*>.*?</pre>', ' ', content_source, flags=re.DOTALL)
        content_no_code = re.sub(r'<code[^>]*>.*?</code>', ' ', content_no_code, flags=re.DOTALL)
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
        # 优先使用已渲染的 HTML（p.content），若为空或看起来不是 HTML，则回退渲染可用的原始 Markdown（content_raw 或 p.content）
        content_source = p.content or ''
        if not content_source or '<' not in content_source:
            raw_fallback = getattr(p, 'content_raw', '') or p.content or ''
            if raw_fallback:
                content_source = markdownify(raw_fallback)
            else:
                content_source = p.content or ''

        # 移除代码块（<pre> 和 <code>）并清理标签与空白，生成摘要
        content_no_code = re.sub(r'<pre[^>]*>.*?</pre>', ' ', content_source, flags=re.DOTALL)
        content_no_code = re.sub(r'<code[^>]*>.*?</code>', ' ', content_no_code, flags=re.DOTALL)
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
