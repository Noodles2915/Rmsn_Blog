from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from users.views import get_current_user
from .models import Follow, Notification, Message
from users.models import User
from django.urls import reverse
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType


@require_POST
def toggle_follow(request, username):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': '请先登录'}, status=401)
    target = get_object_or_404(User, username=username)
    if target.id == user.id:
        return JsonResponse({'ok': False, 'error': '不能关注自己'}, status=400)
    obj, created = Follow.objects.get_or_create(follower=user, followed=target)
    if not created:
        # 已存在 -> 取消关注
        obj.delete()
        following = False
    else:
        following = True
        # 创建通知，target 指向被关注的用户
        try:
            ct = ContentType.objects.get_for_model(target.__class__)
            Notification.objects.create(user=target, actor=user, verb=f"关注了你", target_content_type=ct, target_object_id=str(target.id))
        except Exception:
            Notification.objects.create(user=target, actor=user, verb=f"关注了你")
    followers_count = Follow.objects.filter(followed=target).count()
    return JsonResponse({'ok': True, 'following': following, 'followers_count': followers_count})


def notifications_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('users:login')
    qs = Notification.objects.filter(user=user).order_by('-created_at')[:50]
    return render(request, 'notifications_list.html', {'notifications': qs, 'user': user})


@require_POST
def mark_notification_read(request, nid=None):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': '请先登录'}, status=401)
    if nid:
        n = get_object_or_404(Notification, id=nid, user=user)
        n.unread = False
        n.save(update_fields=['unread'])
        return JsonResponse({'ok': True})
    else:
        Notification.objects.filter(user=user, unread=True).update(unread=False)
        return JsonResponse({'ok': True})


def notifications_count(request):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': True, 'count': 0})
    c = Notification.objects.filter(user=user, unread=True).count()
    return JsonResponse({'ok': True, 'count': c})


def messages_count(request):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': True, 'count': 0})
    # 未读私信数（收件箱中未读）
    c = Message.objects.filter(recipient=user, is_read=False).count()
    return JsonResponse({'ok': True, 'count': c})


def messages_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('users:login')
    # 简单列出近50条与该用户相关的会话（按最新消息排序）
    qs = Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-created_at')[:100]
    return render(request, 'messages_list.html', {'messages': qs, 'user': user})


@require_POST
def send_message(request, username):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': '请先登录'}, status=401)
    recipient = get_object_or_404(User, username=username)
    content = request.POST.get('content') or request.body.decode('utf-8')
    content = content.strip()
    if not content:
        return JsonResponse({'ok': False, 'error': '消息内容不能为空'}, status=400)
    msg = Message.objects.create(sender=user, recipient=recipient, content=content)
    # 创建通知给收件人，target 指向消息
    try:
        ct = ContentType.objects.get_for_model(msg.__class__)
        Notification.objects.create(user=recipient, actor=user, verb='向你发送了私信', target_content_type=ct, target_object_id=str(msg.id))
    except Exception:
        Notification.objects.create(user=recipient, actor=user, verb='向你发送了私信')
    return JsonResponse({'ok': True, 'message_id': str(msg.id)})
from django.shortcuts import render

# Create your views here.
