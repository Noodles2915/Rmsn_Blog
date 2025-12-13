from django.shortcuts import render, redirect
from .models import User, UserSession
from django.http import JsonResponse, HttpResponse
from .forms import RegistrationForm, LoginForm, ProfileEditForm
from utils.email import send_verification_email
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
import time

# 回退的进程内速率记录（仅用于开发/无 cache 环境，非跨进程）
_IP_RATE_MAP = {}



def get_current_user(request):
    """获取当前登录用户"""
    session_token = request.COOKIES.get('session_token')
    if not session_token:
        return None
    
    try:
        session = UserSession.objects.get(
            session_token=session_token,
            is_active=True
        )
        if session.is_valid():
            return session.user
        else:
            session.is_active = False
            session.save()
    except UserSession.DoesNotExist:
        pass
    
    return None

def require_login(view_func):
    """登陆装饰器"""
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return redirect('login')
        request.user = user
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    if get_current_user(request):
        return redirect('users:dashboard')
    else:
        return redirect('users:login')
    
def login(request):
    # 如果已登录，跳转到站点首页或仪表盘
    if get_current_user(request):
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                if user.verify_password(password):
                    token = UserSession.create_session(user)
                    response = redirect('index')
                    # cookie 保持与 session 有效期一致（7 天）
                    response.set_cookie('session_token', token, max_age=7*24*3600, httponly=True)
                    return response
                else:
                    form.add_error(None, '用户名或密码错误')
            except User.DoesNotExist:
                form.add_error(None, '用户名或密码错误')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register(request):
    if get_current_user(request):
        return redirect('index')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request=request)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # 检查用户名/邮箱是否存在
            if User.objects.filter(username=username).exists():
                form.add_error('username', '该用户名已被占用')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', '该邮箱已被注册')
            else:
                user = User(username=username, email=email)
                user.password_encrypt(password)
                user.save()
                token = UserSession.create_session(user)
                response = redirect('index')
                response.set_cookie('session_token', token, max_age=7*24*3600, httponly=True)
                return response
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def dashboard(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    
    # 获取用户发布的文章统计
    from posting.models import Post
    user_posts = Post.objects.filter(author=user).order_by('-created_at')[:5]
    posts_count = Post.objects.filter(author=user).count()
    comments_count = 0  # 后续可以扩展
    views_count = 0  # 后续可以扩展
    
    context = {
        'user': user,
        'user_posts': user_posts,
        'posts_count': posts_count,
        'comments_count': comments_count,
        'views_count': views_count,
    }
    return render(request, 'dashboard.html', context)

def profile(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    
    # 获取用户统计信息
    from posting.models import Post
    posts_count = Post.objects.filter(author=user).count()
    comments_count = 0  # 后续可以扩展
    views_count = 0  # 后续可以扩展
    
    context = {
        'user': user,
        'posts_count': posts_count,
        'comments_count': comments_count,
        'views_count': views_count,
    }
    return render(request, 'profile.html', context)

def profile_edit(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileEditForm(instance=user)

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'profile_edit.html', context)

def logout(request):
    # 注销当前会话
    session_token = request.COOKIES.get('session_token')
    response = redirect('index')
    if session_token:
        try:
            session = UserSession.objects.get(session_token=session_token, is_active=True)
            session.is_active = False
            session.save()
        except UserSession.DoesNotExist:
            pass
        response.delete_cookie('session_token')
    return response


@require_POST
def send_verification_code(request):
    """AJAX 接口：接收 `email`，为该邮箱生成并发送验证码，保存到 session。"""
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'ok': False, 'error': '缺少 email'}, status=400)

    # 基于 IP 的速率限制（防止批量滥用）
    # 规则：每个 IP 每小时最多允许 10 次发送（可按需调整）。
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    IP_LIMIT = 10
    IP_WINDOW = 60 * 60
    now_ts = int(time.time())
    ip_key = f'vcode_ip_{client_ip}'

    try:
        records = cache.get(ip_key)
    except Exception:
        records = None

    if records is None:
        # 回退到进程内存
        records = _IP_RATE_MAP.get(ip_key, [])

    # 过滤过期记录
    records = [t for t in records if now_ts - int(t) < IP_WINDOW]
    if len(records) >= IP_LIMIT:
        # 已达上限，计算下次可用时间
        oldest = min(records)
        retry_after = IP_WINDOW - (now_ts - int(oldest))
        return JsonResponse({'ok': False, 'error': '请求过于频繁，请稍后再试', 'retry_after': retry_after}, status=429)

    # 记录此次请求时间（将在发送成功后写回缓存）
    records.append(now_ts)
    try:
        cache.set(ip_key, records, timeout=IP_WINDOW)
    except Exception:
        _IP_RATE_MAP[ip_key] = records

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'ok': False, 'error': '邮箱格式不正确'}, status=400)

    # 若邮箱已被注册，返回错误
    if User.objects.filter(email=email).exists():
        return JsonResponse({'ok': False, 'error': '该邮箱已被注册'}, status=400)
    # 冷却检查：若上次发送时间小于 COOLDOWN 秒，则拒绝并返回剩余秒数
    session_key = f'email_vcode_{email}'
    prev = request.session.get(session_key)
    now = int(time.time())
    COOLDOWN = 60
    if isinstance(prev, dict):
        ts = prev.get('ts')
        if ts and (now - int(ts) < COOLDOWN):
            retry_after = COOLDOWN - (now - int(ts))
            return JsonResponse({'ok': False, 'error': '请稍后再试', 'retry_after': retry_after}, status=429)

    try:
        send_verification_email(email, request)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)