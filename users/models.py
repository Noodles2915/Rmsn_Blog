# auth/models.py
# 没错，我闲的没事又重新实现了一次用户模型，因为我疯了。

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