from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from users.views import get_current_user
from .models import Post, Tag

def new_post(request):
    """发布新文章"""
    user = get_current_user(request)
    if not user:
        return redirect('users:login')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        tags_str = request.POST.get('tags', '').strip()
        action = request.POST.get('action', 'publish')
        
        if not title or not content:
            return render(request, 'new_post.html', {
                'error': '标题和内容不能为空'
            })
        
        # 创建文章
        post = Post.objects.create(
            title=title,
            content=content,
            author=user
        )
        
        # 处理标签
        if tags_str:
            for tag_name in tags_str.split(','):
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
        
        return redirect('users:dashboard')
    
    return render(request, 'new_post.html')

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
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        tags_str = request.POST.get('tags', '').strip()
        
        if not title or not content:
            return render(request, 'edit_post.html', {
                'post': post,
                'error': '标题和内容不能为空'
            })
        
        # 更新文章
        post.title = title
        post.content = content
        post.save()
        
        # 更新标签
        post.tags.clear()
        if tags_str:
            for tag_name in tags_str.split(','):
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
        
        return redirect('users:dashboard')
    
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
