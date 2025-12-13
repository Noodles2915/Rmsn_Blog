from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from users.views import get_current_user
from .models import Post, Tag, Comment
from .forms import PostForm, CommentForm, ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from markdownx.utils import markdownify
import bleach


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
            form.save_m2m()
            return redirect('users:dashboard')
        else:
            return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})

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
            form.save_m2m()
            return redirect('users:dashboard')
        else:
            return render(request, 'edit_post.html', {'post': post, 'form': form})
    
    context = {
        'post': post,
        'form': None,
    }
    return render(request, 'edit_post.html', context)

def view_post(request, post_id):
    """查看文章详情"""
    post = get_object_or_404(Post, id=post_id)
    
    context = {
        'post': post,
        'comments': post.comments.filter(level=0).order_by('-created_at'),
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
