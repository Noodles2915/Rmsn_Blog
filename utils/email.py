from random import randint
import time
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code():
    """生成一个6位验证码."""
    vcode = randint(0, 999999)
    return f"{vcode:06d}"


def send_verification_email(email: str, request, subject: str = None, expire_seconds: int = 300) -> str:
    """生成验证码、发送邮件并把验证码和时间戳保存在 session 中。

    返回生成的验证码（便于测试）。
    """
    code = generate_verification_code()
    subject = subject or '注册验证码 - RmsnBlog'
    message = f'您的注册验证码为: {code}，有效期 {expire_seconds//60} 分钟。'
    from_email = settings.EMAIL_HOST_USER

    # 发送邮件（如配置无效会抛异常）
    send_mail(subject, message, from_email, [email], fail_silently=False)

    # 保存到 session，带上时间戳用于过期校验
    session_key = f'email_vcode_{email}'
    request.session[session_key] = {'code': code, 'ts': int(time.time()), 'expire': expire_seconds}
    request.session.modified = True

    return code
