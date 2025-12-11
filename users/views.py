from django.shortcuts import render, redirect
from .models import User, UserSession
from django.http import JsonResponse, HttpResponse
from .forms import RegistrationForm, LoginForm



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
        return redirect('dashboard')
    else:
        return redirect('login')
    
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
        form = RegistrationForm(request.POST)
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


def logout(request):
    # 注销当前会话
    session_token = request.COOKIES.get('session_token')
    response = redirect('login')
    if session_token:
        try:
            session = UserSession.objects.get(session_token=session_token, is_active=True)
            session.is_active = False
            session.save()
        except UserSession.DoesNotExist:
            pass
        response.delete_cookie('session_token')
    return response