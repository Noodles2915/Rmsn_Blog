
# RmsnBlog

For English readers：[English](README_EN.md)

简体中文说明 — 一个基于 Django 的简单博客示例项目。项目仅依赖 Django 本身。

**项目状态**: 教学/示例用途。适合学习 Django 项目结构、用户管理与简单帖子发布。

**主要目录**:
- `RmsnBlog/`: Django 项目配置（`settings.py`, `urls.py`, `wsgi.py` 等）。
- `posting/`: 博客帖子相关的 app（models、views、templates 等）。
- `users/`: 用户相关的 app（注册、登录、用户模型或表单）。
- `templates/`: 全局模板目录，包含 `index.html`, `login.html`, `register.html` 等。
- `manage.py`: Django 管理脚本。

**依赖**:
- 仅需 `Django`（推荐使用与本机 Python 兼容的稳定版本，例如 `django>=3.2` 或 `django>=4.x`，视你的环境而定）。

示例 `requirements.txt`（可选）:
```
Django
```

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

**运行测试**
- 使用 Django 测试命令: `python manage.py test`。

**项目说明（简要）**
- 配置位于 `RmsnBlog/settings.py`。可在此调整 `INSTALLED_APPS`、模板路径、数据库（默认 SQLite）等。
- URL 路由定义在 `RmsnBlog/urls.py`，各 app 也有自己的 `urls.py`（如 `users/urls.py`）。
- `posting` app 存放与帖子相关的逻辑；`users` app 管理用户登录/注册逻辑。
- 模板文件主要放在项目根下的 `templates/` 以及各 app 的 `templates/` 子目录。

**部署提示（简要）**
- 生产环境请使用 WSGI/ASGI 容器（如 Gunicorn + Nginx 或 Daphne + Nginx），并配置 `DEBUG=False` 与安全设置（`ALLOWED_HOSTS`、静态文件、数据库等）。
- 在部署前运行 `python manage.py collectstatic`（若使用静态文件）。

**常见命令速查**
- 迁移: `python manage.py migrate`
- 创建迁移: `python manage.py makemigrations`
- 运行开发服务器: `python manage.py runserver`
- 创建超级用户: `python manage.py createsuperuser`
- 运行测试: `python manage.py test`

**文件/目录索引（快速参考）**
- `manage.py` — 项目管理命令入口。
- `RmsnBlog/settings.py` — 全局配置。
- `RmsnBlog/urls.py` — 主路由表。
- `posting/` — 博客 app（模型、视图、表单、管理面板相关）。
- `users/` — 用户相关逻辑（登录、注册、表单）。
- `templates/` — 全局模板文件。

---

## 邮件（SMTP）配置

本项目的邮箱验证码功能依赖 Django 的邮件发送能力。请在运行前通过环境变量或直接在 `RmsnBlog/settings.py` 中配置下列变量：

- `EMAIL_BACKEND`：开发时可用 `django.core.mail.backends.console.EmailBackend`（将邮件打印到控制台）或 `django.core.mail.backends.smtp.EmailBackend`（真实发送）。
- `EMAIL_HOST`：SMTP 服务器地址（例如 `smtp.gmail.com`）。
- `EMAIL_PORT`：SMTP 端口（通常 587 用于 TLS）。
- `EMAIL_HOST_USER`：发信邮箱用户名（通常为完整邮箱地址）。
- `EMAIL_HOST_PASSWORD`：发信邮箱密码或应用专用密码。
- `EMAIL_USE_TLS`：是否使用 TLS（布尔值）。

建议在生产环境通过环境变量设置，上面项目的 `RmsnBlog/settings.py` 已读取这些环境变量。示例（Windows PowerShell 临时设置）：

```powershell
$env:EMAIL_HOST='smtp.example.com'
$env:EMAIL_PORT='587'
$env:EMAIL_HOST_USER='your@domain.com'
$env:EMAIL_HOST_PASSWORD='your_smtp_password'
$env:EMAIL_USE_TLS='True'
```

开发调试提示：
- 若只是本地开发且不想发送真实邮件，可以把 `EMAIL_BACKEND` 设置为 `django.core.mail.backends.console.EmailBackend`，这样发送的邮件会输出到控制台，便于查看验证码。示例：在 `RmsnBlog/settings.py` 临时修改：

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

- 对于 Gmail 等服务，通常需要启用“应用专用密码”或降低安全级别（不推荐）。请参考你所使用邮箱服务商的 SMTP 配置说明。

安全提示：不要在源码中写明明文密码，优先使用环境变量或秘密管理服务。

## 速率限制说明（验证码发送）

项目对邮箱验证码发送做了多层速率限制以防滥用：

- 每个邮箱的验证码有 60 秒冷却（前端/后端均有校验）。
- 每个 IP 最多每小时允许 10 次发送（服务器端限制，若超过会返回 HTTP 429 并包含 `retry_after` 字段，表示应等待的秒数）。

如果需要更严格或更复杂的限流（例如基于用户、基于账号、或使用 Redis/外部速率限制服务），建议在 `send_verification_code` 处扩展并使用 Redis/缓存层实现全局一致性。
