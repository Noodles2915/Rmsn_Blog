from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from users.views import get_current_user
from .models import Post, Tag, Comment
from .forms import PostForm, CommentForm, ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from markdownx.utils import markdownify
import bleach
import json
from django.utils.html import strip_tags
from django.utils.text import Truncator


def new_post(request):
    """发布新文章"""
    user = get_current_user(request)
    if not user:
        return redirect('users:login')

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # 将 Markdown 渲染为 HTML 并清理 XSS
            html = markdownify(form.cleaned_data['content'])
            cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
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
        if form.is_valid():
            post = form.save(commit=False)
            html = markdownify(form.cleaned_data['content'])
            cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
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

    # 评论与文章为独立模型时，不应依赖反向属性，改为直接查询 Comment
    comments = Comment.objects.filter(post=post, level=0).order_by('-created_at').prefetch_related('replies')

    context = {
        'post': post,
        'comments': comments,
        'tags': tags,
        'is_updated': is_updated,
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
            parent = Comment.objects.get(id=int(parent_id), post=post)
            level = parent.level + 1
        except Exception:
            parent = None
            level = 0

    user = get_current_user(request)
    author = user.username if user else request.POST.get('author', '匿名')

    raw_md = form.cleaned_data['content']
    html = markdownify(raw_md)
    cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

    comment = Comment.objects.create(
        post=post,
        parent=parent,
        level=level,
        author=author,
        content=cleaned,
    )

    # 支持 AJAX：返回渲染后的 HTML 片段以便局部刷新
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        rendered = render_to_string('_comment.html', {'comment': comment, 'offset': level * 24, 'post': post}, request=request)
        return JsonResponse({'ok': True, 'html': rendered, 'comment_id': comment.id, 'parent_id': parent.id if parent else None})

    return redirect('posting:view_post', post_id=post_id)

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
