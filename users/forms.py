from typing import Any
from django.forms import Form, CharField, EmailField, PasswordInput
from .models import User
from django import forms
from utils.email import generate_verification_code as gvc
import time

class RegistrationForm(Form):
    username = CharField(label="用户名",max_length=150, required=True)
    email = EmailField(label="邮箱",required=True)
    verification_code = CharField(label="邮箱验证码", max_length=6, required=True)
    password = CharField(label="密码",widget=PasswordInput, required=True)
    confirm_password = CharField(label="确认密码",widget=PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        # 接收 view 传入的 request 用于读取 session 中的验证码
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "两次输入的密码不匹配.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email

    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        email = self.cleaned_data.get('email')

        if not self.request:
            raise forms.ValidationError('无法验证验证码（无效请求）')

        session_key = f'email_vcode_{email}' if email else None
        expected = None
        if session_key:
            expected = self.request.session.get(session_key)

        if not expected:
            raise forms.ValidationError('验证码不存在或已过期')

        # 支持两种 session 保存格式：旧的直接保存 code 字符串，或新的 dict 包含 code/ts/expire
        expected_code = None
        if isinstance(expected, dict):
            expected_code = expected.get('code')
            ts = expected.get('ts')
            expire = expected.get('expire', 300)
            if ts is None:
                raise forms.ValidationError('验证码数据不完整')
            if int(time.time()) - int(ts) > int(expire):
                # 过期
                try:
                    del self.request.session[session_key]
                except Exception:
                    pass
                raise forms.ValidationError('验证码已过期')
        else:
            expected_code = expected

        if code != expected_code:
            raise forms.ValidationError('验证码不正确')

        # 验证通过后移除，避免重复使用
        try:
            del self.request.session[session_key]
        except Exception:
            pass

        return code
    


class LoginForm(Form):
    username = CharField(label="用户名",max_length=150, required=True)
    password = CharField(label="密码",widget=PasswordInput, required=True)


class RequestPasswordResetForm(Form):
    """请求密码重置表单（第一步：输入邮箱获取验证码）"""
    email = EmailField(label="邮箱", required=True)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱未注册')
        return email


class PasswordResetForm(Form):
    """密码重置表单（第二步：验证码+新密码）"""
    verification_code = CharField(label="验证码", max_length=6, required=True)
    password = CharField(label="新密码", widget=PasswordInput, required=True)
    confirm_password = CharField(label="确认新密码", widget=PasswordInput, required=True)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            self.add_error('confirm_password', "两次输入的密码不匹配")
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    # 允许不提交 theme（前端有独立的客户端主题控制），避免表单因为缺少该字段而整体验证失败
    theme = forms.ChoiceField(choices=User.THEME_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['email', 'avatar', 'bg', 'bio', 'theme']
        labels = {
            'email': '邮箱',
            'avatar': '头像',
            'bg': '背景图片',
            'bio': '个人简介',
            'theme': '显示主题',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '输入个人简介，最多 500 个字符',
            }),
            'theme': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('头像文件不能超过5MB')
            if not avatar.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise forms.ValidationError('仅支持jpg、jpeg、png、gif格式的图片')
        return avatar

    def clean_bg(self):
        bg = self.cleaned_data.get('bg')
        if bg:
            if bg.size > 8 * 1024 * 1024:
                raise forms.ValidationError('背景文件不能超过8MB')
            if not bg.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise forms.ValidationError('背景仅支持图片文件（jpg、png、gif）')
        return bg
