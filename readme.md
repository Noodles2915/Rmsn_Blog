
# RmsnBlog

For English Readers:[English](README_EN.md)

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

**静态脚本**
本项目使用了网络上的静态脚本，由于无法确定开源协议是否允许在其它项目中挂载对应脚本，因此将相关内容放在下方.

## 本地 JavaScript 和 CSS 资源清单

### marked.min.js
- **来源**: https://cdn.jsdelivr.net/npm/marked/marked.min.js
- **版本**: Latest (4.x)
- **用途**: Markdown 文本解析器，用于实时预览 Markdown 内容
- **使用位置**:
  - `templates/new_post.html` - 发布新文章时实时预览
  - `templates/edit_post.html` - 编辑文章时实时预览

### cropper.min.css
- **来源**: https://cdn.jsdelivr.net/npm/cropperjs@1.5.13/dist/cropper.min.css
- **版本**: 1.5.13
- **用途**: 图片裁剪工具的样式文件
- **使用位置**: `templates/profile_edit.html` - 头像和背景图片裁剪

### cropper.min.js
- **来源**: https://cdn.jsdelivr.net/npm/cropperjs@1.5.13/dist/cropper.min.js
- **版本**: 1.5.13
- **用途**: 图片裁剪工具的功能脚本
- **使用位置**: `templates/profile_edit.html` - 头像和背景图片裁剪

## 说明

所有文件都已通过模板中的 Django `{% static %}` 标签引用，确保在生产环境中可以正确加载。

### 更新方法：

如需更新这些文件，可以使用以下命令：

```bash
# 更新 marked.js
powershell -Command "Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/marked/marked.min.js' -OutFile 'static/netscript/marked.min.js'"

# 更新 cropper.min.css
powershell -Command "Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/cropperjs@1.5.13/dist/cropper.min.css' -OutFile 'static/netscript/cropper.min.css'"

# 更新 cropper.min.js
powershell -Command "Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/cropperjs@1.5.13/dist/cropper.min.js' -OutFile 'static/netscript/cropper.min.js'"
```

## 许可证

这些库遵循各自的开源许可证：
- **marked.js**: MIT License
- **cropperjs**: MIT License

## 验证码速率限制

项目对验证码请求应用了多层速率限制以防止滥用：

- **单邮箱冷却时间**: 60 秒（客户端和服务器均进行检查）
- **IP 限制**: 默认每小时 10 次发送限制（服务器端）。超过限制时，端点返回 HTTP 429，并在响应中包含 `retry_after` 字段，指示需要等待的秒数。

如需更强大或分布式的速率限制（例如基于 Redis 的计数器或外部速率限制服务），可扩展 `send_verification_code` 函数以使用共享缓存或 Redis。

---
