# Django Starter (apps/ + Tailwind)

Starter setup Django dengan:

- `apps/` untuk semua Django apps
- `config/settings/` terpisah: `base`, `dev`, `staging`, `prod`
- pindah environment cukup ubah `DJANGO_ENV=dev|staging|prod`
- integrasi `django-tailwind`

## Struktur

```text
.
├── manage.py
├── apps/
├── theme/
├── static/
└── config/
    └── settings/
        ├── __init__.py
        ├── base.py
        ├── dev.py
        ├── staging.py
        └── prod.py
```

## Switch Environment

`Rename env.example to .env`

```bash
DJANGO_ENV=prod/dev/staging
```

## Buat App Baru (di `apps/`)

```bash
python manage.py startapp yournewapps apps/yournewapps
```

Daftarkan ke `LOCAL_APPS` (di `config/settings/base.py`):

```py
LOCAL_APPS = [
    "apps.yournewapps"
]
```

## Instalation Django + tailwindcss built in

Install:

```bash
pip install -r requirements.txt
```

`tailwindcss apps in`
```py
THIRD_PARTY_APPS = [
    "tailwind",
    "theme",
]
```

Init + install + run Tailwind:

```bash
python manage.py tailwind install
python manage.py tailwind start
```

## Load Tailwind di Template

in templates (ex: `templates/base.html`):

```django
{% load tailwind_tags %}
{% tailwind_css %}
```

## Run Server

```bash
python manage.py runserver
```
