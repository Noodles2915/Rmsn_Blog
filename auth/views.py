from django.shortcuts import render,redirect
from .models import User,UserSession
from django.http import JsonResponse,HttpResponse

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
    pass