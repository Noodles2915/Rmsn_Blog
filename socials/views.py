from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
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
        # 创建通知，不需要 target 因为 actor 已经指向被关注的用户
        Notification.objects.create(user=target, actor=user, verb=f"关注了你")
    followers_count = Follow.objects.filter(followed=target).count()
    return JsonResponse({'ok': True, 'following': following, 'followers_count': followers_count})


def notifications_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('users:login')
    qs = Notification.objects.filter(user=user).order_by('-created_at')
    # Mark all unread notifications as read when user views the list
    Notification.objects.filter(user=user, unread=True).update(unread=False)
    
    # Pagination: 10 per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications_list.html', {
        'notifications': page_obj,
        'page_obj': page_obj,
        'user': user
    })


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
    
    # 查看与特定用户的对话
    chat_with = request.GET.get('with')
    if chat_with:
        try:
            other_user = User.objects.get(username=chat_with)
            # 标记来自对方的未读消息为已读
            Message.objects.filter(sender=other_user, recipient=user, is_read=False).update(is_read=True)
            # 获取双方的所有消息
            qs = Message.objects.filter(
                Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
            ).order_by('created_at')
            # 分页
            page_number = request.GET.get('page', 1)
            paginator = Paginator(qs, 50)
            page_obj = paginator.get_page(page_number)
            return render(request, 'messages_chat.html', {
                'messages': page_obj,
                'page_obj': page_obj,
                'other_user': other_user,
                'user': user
            })
        except User.DoesNotExist:
            pass
    
    # 获取所有对话列表（按最后一条消息时间排序）
    # 获取所有相关用户
    user_ids = set()
    msgs = Message.objects.filter(Q(sender=user) | Q(recipient=user)).values('sender_id', 'recipient_id')
    for m in msgs:
        user_ids.add(m['sender_id'])
        user_ids.add(m['recipient_id'])
    user_ids.discard(user.id)
    
    # 为每个对话伙伴获取最后一条消息
    conversations = []
    for uid in user_ids:
        other = User.objects.get(id=uid)
        last_msg = Message.objects.filter(
            Q(sender=user, recipient=other) | Q(sender=other, recipient=user)
        ).order_by('-created_at').first()
        if last_msg:
            unread_count = Message.objects.filter(sender=other, recipient=user, is_read=False).count()
            conversations.append({
                'other_user': other,
                'last_message': last_msg,
                'unread_count': unread_count,
            })
    
    # 按最后消息时间排序
    conversations.sort(key=lambda x: x['last_message'].created_at, reverse=True)
    
    return render(request, 'messages_list.html', {'conversations': conversations, 'user': user})


@require_POST
def send_message(request, username):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': '请先登录'}, status=401)
    recipient = get_object_or_404(User, username=username)
    
    # 支持JSON和表单两种格式
    try:
        import json
        payload = json.loads(request.body.decode('utf-8'))
        content = payload.get('content', '')
    except:
        content = request.POST.get('content', '')
    
    content = content.strip()
    if not content:
        return JsonResponse({'ok': False, 'error': '消息内容不能为空'}, status=400)
    
    msg = Message.objects.create(sender=user, recipient=recipient, content=content)
    
    # 创建通知给收件人
    try:
        ct = ContentType.objects.get_for_model(msg.__class__)
        Notification.objects.create(user=recipient, actor=user, verb='向你发送了私信', target_content_type=ct, target_object_id=str(msg.id))
    except Exception:
        Notification.objects.create(user=recipient, actor=user, verb='向你发送了私信')
    
    return JsonResponse({
        'ok': True,
        'message': {
            'id': str(msg.id),
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'sender': user.username,
            'sender_avatar': user.avatar_url,
        }
    })
from django.shortcuts import render

# Create your views here.
