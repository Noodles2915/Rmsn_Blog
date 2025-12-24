from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from users.views import get_current_user
from .models import Post, Tag, Comment, PostLike
from .forms import PostForm, CommentForm, ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from markdownx.utils import markdownify
import bleach
import re
import html as pyhtml
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
import json
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse


def highlight_code_blocks(html_input):
    fmt = HtmlFormatter(cssclass='codehilite')
    pattern = re.compile(r'<pre><code(?: class="language-([^"]+)")?>(.*?)</code></pre>', re.DOTALL)
    def _repl(m):
        lang = m.group(1)
        code = pyhtml.unescape(m.group(2) or '')
        try:
            if lang:
                lexer = get_lexer_by_name(lang, stripall=True)
            else:
                lexer = guess_lexer(code)
        except ClassNotFound:
            from pygments.lexers.special import TextLexer
            lexer = TextLexer()
        return highlight(code, lexer, fmt)
    return pattern.sub(_repl, html_input)


def new_post(request):
    """发布新文章"""
    user = get_current_user(request)
    if not user:
        return redirect('users:login')

    if request.method == 'POST':
        form = PostForm(request.POST)
        # 手动获取内容
        raw_md = request.POST.get('content', '').strip()
        
        if not raw_md:
            # content 为空，重新渲染表单并显示错误
            form.add_error('content', '文章内容不能为空')
            tags_raw = request.POST.get('tags', '')
            tags_list = [t.strip() for t in tags_raw.split(',') if t.strip()]
            return render(request, 'new_post.html', {'form': form, 'initial_tags_json': json.dumps(tags_list)})
        
        if form.is_valid():
            post = form.save(commit=False)
            post.content_raw = raw_md
            # 将 Markdown 渲染为 HTML 并清理 XSS
            html = markdownify(raw_md)
            # Server-side syntax highlighting (applies module-level helper)
            highlighted = highlight_code_blocks(html)
            cleaned = bleach.clean(highlighted, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
            post.content = cleaned
            post.author = user
            post.save()
            # 解析并创建/关联自定义标签（前端通过隐藏字段提交逗号分隔的标签名）
            tags_raw = request.POST.get('tags', '')
            if tags_raw:
                tag_names = [t.strip() for t in tags_raw.split(',') if t.strip()]
                tag_objs = []
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name)
                    tag_objs.append(tag_obj)
                post.tags.set(tag_objs)
            else:
                post.tags.clear()
            return redirect('users:dashboard')
        else:
            # 将前端 tags 回显数据也交给模板（视图负责准备初始标签数据）
            tags_raw = request.POST.get('tags', '')
            tags_list = [t.strip() for t in tags_raw.split(',') if t.strip()]
            return render(request, 'new_post.html', {'form': form, 'initial_tags_json': json.dumps(tags_list)})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form, 'initial_tags_json': json.dumps([])})

def edit_post(request, post_id):
    """编辑文章"""
    user = get_current_user(request)
    if not user:
        return redirect('users:login')
    
    post = get_object_or_404(Post, id=post_id)
    
    # 检查权限：只能编辑自己的文章
    if post.author != user:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        # 手动获取内容
        raw_md = request.POST.get('content', '').strip()
        
        if not raw_md:
            # content 为空，重新渲染表单并显示错误
            form.add_error('content', '文章内容不能为空')
            tags_raw = request.POST.get('tags', '')
            tags_list = [t.strip() for t in tags_raw.split(',') if t.strip()]
            return render(request, 'edit_post.html', {'post': post, 'form': form, 'initial_tags_json': json.dumps(tags_list)})
        
        if form.is_valid():
            post = form.save(commit=False)
            # 获取表单中的 content（原始 Markdown）
            post.content_raw = raw_md
            # 将 Markdown 渲染为 HTML 并清理 XSS
            html = markdownify(raw_md)
            # 高亮后清理
            highlighted = highlight_code_blocks(html)
            cleaned = bleach.clean(highlighted, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
            post.content = cleaned
            post.save()
            # 更新标签
            tags_raw = request.POST.get('tags', '')
            if tags_raw:
                tag_names = [t.strip() for t in tags_raw.split(',') if t.strip()]
                tag_objs = []
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name)
                    tag_objs.append(tag_obj)
                post.tags.set(tag_objs)
            else:
                post.tags.clear()
            return redirect('users:dashboard')
        else:
            tags_raw = request.POST.get('tags', '')
            tags_list = [t.strip() for t in tags_raw.split(',') if t.strip()]
            return render(request, 'edit_post.html', {'post': post, 'form': form, 'initial_tags_json': json.dumps(tags_list)})
    
    # 预构建初始标签数据，以便模板不需要进行复杂的 tags 拼接
    initial_tags = [t.name for t in post.tags.all()]
    context = {
        'post': post,
        'form': PostForm(instance=post),
        'initial_tags_json': json.dumps(initial_tags),
    }
    return render(request, 'edit_post.html', context)

def view_post(request, post_id):
    """查看文章详情"""
    post = get_object_or_404(Post, id=post_id)
    
    # 增加浏览量计数
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # 将标签列表与是否有更新之类的轻量信息在视图中计算好，简化模板判断
    tags = list(post.tags.values_list('name', flat=True))
    is_updated = post.updated_at != post.created_at
    
    # 计算预计阅读时间（字数/300，向上取整）
    import math
    content_text = post.content_raw if hasattr(post, 'content_raw') and post.content_raw else post.content
    word_count = len(content_text)
    read_time = math.ceil(word_count / 300) if word_count > 0 else 1

    # 评论与文章为独立模型时，不应依赖反向属性，改为直接查询 Comment
    # 查询顶级评论并预加载所有相关数据
    comments = Comment.objects.filter(post=post, level=0).order_by('-created_at').prefetch_related(
        'author',
        'replies',
        'replies__author'
    )
    
    # 获取当前用户
    user = get_current_user(request)

    # 当前用户是否已点赞此文章
    user_liked = False
    try:
        if user:
            user_liked = PostLike.objects.filter(user=user, post=post).exists()
    except Exception:
        user_liked = False

    context = {
        'post': post,
        'comments': comments,
        'tags': tags,
        'is_updated': is_updated,
        'user': user,
        'user_liked': user_liked,
        'read_time': read_time,
    }
    return render(request, 'post_detail.html', context)


def add_comment(request, post_id):
    """创建评论或回复。支持多级回复。"""
    post = get_object_or_404(Post, id=post_id)
    if request.method != 'POST':
        return redirect('posting:view_post', post_id=post_id)

    form = CommentForm(request.POST)
    if not form.is_valid():
        # 对于 AJAX 请求，返回错误信息；否则回到详情页
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
        return redirect('posting:view_post', post_id=post_id)

    parent_id = request.POST.get('parent_id')
    parent = None
    level = 0
    if parent_id:
        try:
            parent = Comment.objects.get(id=parent_id, post=post)
            level = parent.level + 1
        except (Comment.DoesNotExist, ValueError):
            parent = None
            level = 0

    user = get_current_user(request)
    if not user:
        # 未登录用户不能评论
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': '请先登录后再评论'}, status=401)
        return redirect('users:login')

    raw_md = form.cleaned_data['content']
    html = markdownify(raw_md)
    highlighted = highlight_code_blocks(html)
    cleaned = bleach.clean(highlighted, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

    comment = Comment.objects.create(
        post=post,
        parent=parent,
        level=level,
        author=user,
        content_raw=raw_md,
        content=cleaned,
    )

    # 创建通知：如果发表评论的人不是文章作者，通知文章作者
    try:
        from socials.models import Notification
        from django.contrib.contenttypes.models import ContentType
        # 通知文章作者，target 指向 Post
        if post.author.id != user.id:
            ct = ContentType.objects.get_for_model(post.__class__)
            Notification.objects.create(user=post.author, actor=user, verb='评论了你的文章', target_content_type=ct, target_object_id=str(post.id))
        # 如果是回复，通知父评论作者（且不重复通知文章作者）
        if parent and parent.author.id != user.id and parent.author.id != post.author.id:
            ct_c = ContentType.objects.get_for_model(parent.__class__)
            Notification.objects.create(user=parent.author, actor=user, verb='回复了你的评论', target_content_type=ct_c, target_object_id=str(parent.id))
    except Exception:
        pass

    # 支持 AJAX：返回渲染后的 HTML 片段以便局部刷新
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        rendered = render_to_string('_comment.html', {'comment': comment, 'post': post}, request=request)
        return JsonResponse({'ok': True, 'html': rendered, 'comment_id': str(comment.id), 'parent_id': str(parent.id) if parent else None})

    return redirect('posting:view_post', post_id=post_id)


@require_http_methods(['POST'])
def toggle_like(request, post_id):
    from django.http import JsonResponse
    post = get_object_or_404(Post, id=post_id)
    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': '请先登录'}, status=401)
    try:
        like, created = PostLike.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
            # 创建通知给文章作者
            try:
                from socials.models import Notification
                from django.contrib.contenttypes.models import ContentType
                ct = ContentType.objects.get_for_model(post.__class__)
                if post.author.id != user.id:
                    Notification.objects.create(user=post.author, actor=user, verb='点赞了你的文章', target_content_type=ct, target_object_id=str(post.id))
            except Exception:
                pass
    except Exception:
        return JsonResponse({'ok': False, 'error': '操作失败'}, status=500)

    count = PostLike.objects.filter(post=post).count()
    return JsonResponse({'ok': True, 'liked': liked, 'likes_count': count})

def delete_post(request, post_id):
    """删除文章"""
    user = get_current_user(request)
    if not user:
        return redirect('users:login')
    
    post = get_object_or_404(Post, id=post_id)
    
    # 检查权限：只能删除自己的文章
    if post.author != user:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        post.delete()
        return redirect('users:dashboard')
    
    # GET 请求显示确认页面
    return render(request, 'delete_post_confirm.html', {'post': post})


def tags_autocomplete(request):
    """返回与查询 q 匹配的标签名列表（JSON），用于前端自动完成建议。"""
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        qs = Tag.objects.filter(name__icontains=q).order_by('name')[:20]
    else:
        qs = Tag.objects.all().order_by('name')[:20]
    results = [t.name for t in qs]
    return JsonResponse({'ok': True, 'results': results})


def delete_comment(request, comment_id):
    """删除评论 - 评论作者或文章作者可以删除"""
    user = get_current_user(request)
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': '请先登录'}, status=401)
        return redirect('users:login')
    
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    
    # 检查权限：评论作者或文章作者可以删除
    if comment.author != user and post.author != user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': '无权删除此评论'}, status=403)
        return redirect('posting:view_post', post_id=post.id)
    
    # 删除评论（级联删除所有回复）
    comment.delete()
    
    # AJAX 请求返回 JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'comment_id': comment_id})
    
    # 普通请求重定向回文章页
    return redirect('posting:view_post', post_id=post.id)


def search_posts(request):
    """搜索文章（按标题或标签）- 仅限登录用户"""
    from django.db.models import Q
    from django.core.paginator import Paginator
    from django.urls import reverse
    
    user = get_current_user(request)
    if not user:
        return redirect('users:login')
    
    query = request.GET.get('q', '').strip()
    posts = []
    paginator = None
    page_obj = None
    
    if query:
        # 如果以 # 开头 -> 标签搜索（去掉前缀）；否则仅按标题搜索
        if query.startswith('#'):
            tag = query.lstrip('#').strip()
            if tag:
                qs = Post.objects.filter(
                    Q(tags__name__icontains=tag)
                ).distinct().select_related('author').prefetch_related('tags').order_by('-created_at')
            else:
                qs = Post.objects.none()
        else:
            # 限制查询内容，移除明显的特殊字符以防注入或无效查询
            import re
            safe_q = re.sub(r'[^\w\u4e00-\u9fff\s\-_:,\.\(\)]+', '', query)
            if not safe_q:
                qs = Post.objects.none()
            else:
                qs = Post.objects.filter(
                    Q(title__icontains=safe_q)
                ).distinct().select_related('author').prefetch_related('tags').order_by('-created_at')
        
        # 分页，每页 10 个
        paginator = Paginator(qs, 10)
        page_num = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_num)
        
        # 预处理数据
        for p in page_obj:
            # 移除代码块后再生成摘要
            import re
            clean_content = re.sub(r'<pre[^>]*>.*?</pre>', ' ', p.content)
            clean_content = re.sub(r'\s+', ' ', strip_tags(clean_content)).strip()
            excerpt = Truncator(clean_content).chars(140)
            
            # 获取作者头像 URL
            author_avatar = p.author.avatar.url if p.author.avatar else None
            
            posts.append({
                'id': p.id,
                'title': p.title,
                'url': reverse('posting:view_post', args=[p.id]),
                'author': p.author.username,
                'author_username': p.author.username,
                'author_avatar': author_avatar,
                'created_at': p.created_at,
                'excerpt': excerpt,
                'tags': [{'name': tag.name, 'url': reverse('posting:search_posts') + f'?q=%23{tag.name}'} for tag in p.tags.all()],
            })
    
    context = {
        'user': user,
        'query': query,
        'posts': posts,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'search_results.html', context)


# --------------------
# 解耦后的API视图
# --------------------
def api_post_detail(request, post_id):
    """返回文章的 JSON 表示，包含原始 Markdown 与已渲染 HTML。"""
    post = get_object_or_404(Post, id=post_id)
    data = {
        'id': str(post.id),
        'title': post.title,
        'content_raw': post.content_raw,
        'content': post.content,
        'author': post.author.username,
        'author_avatar': post.author.avatar_url if getattr(post.author, 'avatar_url', None) else '',
        'tags': list(post.tags.values_list('name', flat=True)),
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
        'views_count': post.views_count,
    }
    return JsonResponse({'ok': True, 'post': data})


def api_post_comments(request, post_id):
    """返回文章下的所有评论（扁平列表），供前端渲染线程或树结构。"""
    post = get_object_or_404(Post, id=post_id)
    qs = Comment.objects.filter(post=post).order_by('created_at').select_related('author', 'parent')
    comments = []
    for c in qs:
        comments.append({
            'id': str(c.id),
            'parent': str(c.parent.id) if c.parent else None,
            'level': c.level,
            'author': c.author.username,
            'author_avatar': c.author.avatar_url if getattr(c.author, 'avatar_url', None) else '',
            'author_profile_url': reverse('users:profile_user', args=[c.author.username]),
            'content': c.content,
            'content_raw': getattr(c, 'content_raw', c.content),
            'created_at': c.created_at.isoformat(),
        })
    return JsonResponse({'ok': True, 'comments': comments})


@csrf_exempt
@require_http_methods(['POST'])
def api_add_comment_api(request, post_id):
    """通过 JSON 创建评论（接受 {content, parent_id?}），返回创建后的评论 JSON。"""
    post = get_object_or_404(Post, id=post_id)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'error': 'invalid json'}, status=400)

    raw_md = (payload.get('content') or '').strip()
    if not raw_md:
        return JsonResponse({'ok': False, 'error': 'empty content'}, status=400)

    parent = None
    level = 0
    parent_id = payload.get('parent_id')
    if parent_id:
        try:
            parent = Comment.objects.get(id=parent_id, post=post)
            level = parent.level + 1
        except (Comment.DoesNotExist, ValueError):
            parent = None
            level = 0

    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'authentication required'}, status=401)

    html = markdownify(raw_md)
    highlighted = highlight_code_blocks(html)
    cleaned = bleach.clean(highlighted, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

    comment = Comment.objects.create(
        post=post,
        parent=parent,
        level=level,
        author=user,
        content_raw=raw_md,
        content=cleaned,
    )

    # 创建通知：如果发表评论的人不是文章作者，通知文章作者
    try:
        from socials.models import Notification
        from django.contrib.contenttypes.models import ContentType
        # 通知文章作者，target 指向 Post
        if post.author.id != user.id:
            ct = ContentType.objects.get_for_model(post.__class__)
            Notification.objects.create(user=post.author, actor=user, verb='评论了你的文章', target_content_type=ct, target_object_id=str(post.id))
        # 如果是回复，通知父评论作者（且不重复通知文章作者）
        if parent and parent.author.id != user.id and parent.author.id != post.author.id:
            ct_c = ContentType.objects.get_for_model(parent.__class__)
            Notification.objects.create(user=parent.author, actor=user, verb='回复了你的评论', target_content_type=ct_c, target_object_id=str(parent.id))
    except Exception:
        pass

    data = {
        'id': str(comment.id),
        'parent': str(parent.id) if parent else None,
        'level': comment.level,
        'author': comment.author.username,
        'author_avatar': comment.author.avatar_url if getattr(comment.author, 'avatar_url', None) else '',
        'author_profile_url': reverse('users:profile_user', args=[comment.author.username]),
        'content': comment.content,
        'content_raw': comment.content_raw if hasattr(comment, 'content_raw') else comment.content,
        'created_at': comment.created_at.isoformat(),
    }
    return JsonResponse({'ok': True, 'comment': data})
