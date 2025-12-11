
# RmsnBlog

简体中文说明 — 一个基于 Django 的简单博客示例项目。项目仅依赖 Django 本身（没有额外第三方包）。

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
