
# RmsnBlog

For English Readers:[English](README_EN.md)

简体中文说明 — 一个基于 Django 的简单博客示例项目。

**项目状态**: 教学/示例用途。适合学习 Django 项目结构、用户管理与简单帖子发布。

**主要目录**:
- `RmsnBlog/`: Django 项目配置（`settings.py`, `urls.py`, `wsgi.py` 等）。
- `posting/`: 博客帖子相关的 app（models、views、templates 等）。
- `users/`: 用户相关的 app（注册、登录、用户模型或表单）。
- `templates/`: 全局模板目录，包含 `index.html`, `login.html`, `register.html` 等。
- `manage.py`: Django 管理脚本。
- `social/`: 处理社交内容（私信，通知）。

**依赖**:
- 见`requirements.txt`。


**快速开始（Windows PowerShell）**

1) 创建并激活虚拟环境
```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2) 安装 Django
```
pip install Django
```

3) 应用迁移并创建超级用户
```
python manage.py migrate
python manage.py createsuperuser
```

4) 启动开发服务器
```
python manage.py runserver
```

5) 打开浏览器访问 `http://127.0.0.1:8000/`。

**项目说明**
- 配置位于 `RmsnBlog/settings.py`。可在此调整 `INSTALLED_APPS`、模板路径、数据库（默认 SQLite）等。
- 你需要配置环境变量`DJANGO_SKEY`等，具体见`settings.py`中相关的环境变量调用。
- URL 路由定义在 `RmsnBlog/urls.py`，各 app 也有自己的 `urls.py`（如 `users/urls.py`）。
- `posting` app 存放与帖子相关的逻辑；`users` app 管理用户登录/注册逻辑；`social`app管理用户间的互动通知和私信。
- 模板文件都放在项目根下的 `templates/` 目录中。

**部署提示**
- 生产环境请使用 WSGI/ASGI 容器（如 Gunicorn + Nginx 或 Daphne + Nginx），并配置 `DEBUG=False` 与安全设置（`ALLOWED_HOSTS`、静态文件、数据库等）。
- 在部署前运行 `python manage.py collectstatic`（若使用静态文件）。
- 本项目的模板均使用了**静态css与js**，请在开始部署前根据对应需求下载。
- 注意，这不是一个随时部署的项目，请自行完成一些内容的调整。

 **静态脚本需求**
 ## marked.min.js
- **来源**: https://cdn.jsdelivr.net/npm/marked/marked.min.js
- **版本**: Latest (4.x)
- **用途**: Markdown 文本解析器，用于实时预览 Markdown 内容
- **使用位置**:
  - `templates/new_post.html` - 发布新文章时实时预览
  - `templates/edit_post.html` - 编辑文章时实时预览

## cropper.min.css
- **来源**: https://cdn.jsdelivr.net/npm/cropperjs@1.5.13/dist/cropper.min.css
- **版本**: 1.5.13
- **用途**: 图片裁剪工具的样式文件
- **使用位置**: `templates/profile_edit.html` - 头像和背景图片裁剪

## cropper.min.js
- **来源**: https://cdn.jsdelivr.net/npm/cropperjs@1.5.13/dist/cropper.min.js
- **版本**: 1.5.13
- **用途**: 图片裁剪工具的功能脚本
- **使用位置**: `templates/profile_edit.html` - 头像和背景图片裁剪

## live2d-widget
- **来源**: https://github.com/stevenjoezhang/live2d-widget
- **用途**: 文章详情页面的看板娘
- **使用位置**: `templates/post_detail.html` - 看板娘


---
