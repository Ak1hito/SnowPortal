# SnowPortal

Учебный сайт на Django для подбора сноубордов, просмотра курортов и сохранения досок в избранное.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Открой http://127.0.0.1:8000/. Чтобы добавить доски и курорты через админку, выполни `python manage.py createsuperuser` и зайди на `/admin/`.

По умолчанию используется SQLite. Для PostgreSQL задай `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` и при необходимости `POSTGRES_HOST` и `POSTGRES_PORT`.
