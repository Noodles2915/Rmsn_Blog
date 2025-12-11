# RmsnBlog

English documentation — A minimal Django-based blog example. This project depends only on Django (no other third-party packages).

Project status: Educational / example. Useful to learn Django project structure, basic user management and simple post publishing.

Main directories:
- `RmsnBlog/`: Django project configuration (`settings.py`, `urls.py`, `wsgi.py`, etc.).
- `posting/`: Blog post app (models, views, templates).
- `users/`: User-related app (registration, login, forms).
- `templates/`: Global templates such as `index.html`, `login.html`, `register.html`.
- `manage.py`: Django management script.

Requirements:
- Only `Django` is required. Recommended range: `Django>=4.2,<5`.

Example `requirements.txt` (created in this repo):
```
Django>=4.2,<5
```

Quick start (Windows PowerShell):

1) Create and activate a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2) Install Django
```powershell
pip install -r requirements.txt
```

3) Apply migrations and create a superuser
```powershell
python manage.py migrate
python manage.py createsuperuser
```

4) Run the development server
```powershell
python manage.py runserver
```

5) Visit `http://127.0.0.1:8000/` in your browser.

Run tests:
- Use Django test runner: `python manage.py test`.

Notes on the project:
- Configuration is in `RmsnBlog/settings.py`. Adjust `INSTALLED_APPS`, template dirs, database settings (default: SQLite), etc.
- URL routing is defined in `RmsnBlog/urls.py`. Apps may include their own `urls.py` (e.g., `users/urls.py`).
- The `posting` app contains post-related logic and templates; the `users` app manages registration and login flows.
- Templates live in the project-level `templates/` directory and app-level `templates/` subdirectories.

Deployment hints:
- For production, use a WSGI/ASGI server (e.g., Gunicorn + Nginx or Daphne + Nginx). Set `DEBUG=False`, configure `ALLOWED_HOSTS`, static files and secure settings.
- Run `python manage.py collectstatic` during deployment if you serve static files separately.

Common Django commands:
- Migrate database: `python manage.py migrate`
- Create migrations: `python manage.py makemigrations`
- Run dev server: `python manage.py runserver`
- Create superuser: `python manage.py createsuperuser`
- Run tests: `python manage.py test`

Repository file index (quick reference):
- `manage.py` — entry point for management commands.
- `RmsnBlog/settings.py` — global configuration.
- `RmsnBlog/urls.py` — main URL routing.
- `posting/` — blog app (models, views, admin, templates).
- `users/` — user app (forms, views, urls).
- `templates/` — global templates.

If you want, I can also:
- Pin exact package versions in `requirements.txt` for reproducible installs,
- Add a `Dockerfile` and `docker-compose.yml` for local development,
- Provide a short deployment guide for a platform like Heroku or a Linux server.
