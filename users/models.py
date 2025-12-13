# 没错，我闲的没事又重新实现了一次用户模型，因为我疯了。
try:
    from utils.paths import avatar_upload_path, bg_upload_path
except Exception:
    # 如果直接导入失败（例如包路径问题），将项目根目录加入 sys.path 后重试
    import os
    import sys

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    from utils.paths import avatar_upload_path, bg_upload_path
from django.db import models
from django.utils import timezone
from datetime import timedelta
import hashlib
import uuid

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    salt = models.CharField(max_length=32)
    date_joined = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    bg = models.ImageField(upload_to=bg_upload_path, null=True, blank=True)

    def __str__(self):
        return self.username
    
    def password_encrypt(self,password: str):
        salt = hashlib.md5(self.username.encode('utf-8')).hexdigest()
        self.salt = salt
        hash_pw = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        self.password = hash_pw
    
    def verify_password(self, password: str) -> bool:
        hash_pw = hashlib.sha256((password + self.salt).encode('utf-8')).hexdigest()
        return hash_pw == self.password
    
    @property
    def avatar_url(self) -> str:
        if self.avatar:
            return self.avatar.url
        else:
            return '/static/avatar/blank-pfp.png'
        # 尽管我会随项目上传默认头像文件，但是你可能还是需要稍作修改
        # 毕竟，众口难调。
    
    @property
    def bg_css(self) -> str:
        """返回可直接用于 style="background: ..." 的字符串。
        如果用户上传了背景图，返回 url(...) 的背景设置；否则返回一个默认的非图片渐变背景。
        """
        if self.bg:
            return "url('{}') center/cover no-repeat".format(self.bg.url)
        # 默认非图片背景（渐变）
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

class UserSession(models.Model):
    """用户会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def create_session(user: User) -> str:
        token = uuid.uuid4().hex
        session = UserSession(user=user, session_token=token)
        session.save()
        return token
    
    def is_valid(self) -> bool:
        return self.is_active and (self.created_at + timedelta(days=7) > timezone.now())