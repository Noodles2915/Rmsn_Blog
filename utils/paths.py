import uuid
import os

def avatar_upload_path(instance, filename):
    """头像上传路径生成函数"""
    ext = filename.split('.')[-1]
    fname = f"{uuid.uuid4().hex}.{ext}"

    return os.path.join('avatars',str(instance.id), fname)

def bg_upload_path(instance, filename):
    """背景图片上传路径生成函数"""
    ext = filename.split('.')[-1]
    fname = f"{uuid.uuid4().hex}.{ext}"

    return os.path.join('backgrounds',str(instance.id), fname)

def pic_upload_path(instance, filename):
    """通用图片上传路径生成函数"""
    ext = filename.split('.')[-1]
    fname = f"{uuid.uuid4().hex}.{ext}"

    return os.path.join('pictures', str(instance.id), fname)