# Railway Deployment Guide

This project is ready to run on Railway with Gunicorn and PostgreSQL.

## 1) Create Railway services

1. Create a new Railway project and connect this repository.
2. Add a PostgreSQL service in the same Railway project.
3. In your web service, ensure `railway.json` is detected.

## 2) Configure environment variables

Set these variables in Railway for the web service:

- `DEBUG=False`
- `SECRET_KEY=<strong-random-secret>`
- `DATABASE_URL=<from Railway PostgreSQL>`
- `ALLOWED_HOSTS=<your-service>.up.railway.app,<your-domain>`
- `CSRF_TRUSTED_ORIGINS=https://<your-service>.up.railway.app,https://<your-domain>`
- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS=31536000`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- `SECURE_HSTS_PRELOAD=True`
- `ADMIN_USERNAME=<admin-username>`
- `ADMIN_EMAIL=<admin-email>`
- `ADMIN_PASSWORD=<admin-password>`
- `SEED_DATA_ON_DEPLOY=False`
- `SEED_FIXTURE_PATH=render_seed.json`

You can use `.env.example` as a template.

## 3) Run management commands after first deploy

Run these commands from the Railway web service shell:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py bootstrap_inventory_data
python manage.py create_default_superuser
```

## 4) Verify deployment

1. Open the app URL and check dashboard/login pages.
2. Log in to `/admin/`.
3. Confirm inventory and sales data can be created.
4. Confirm static files are loading.

## 5) One-time production data seed (optional)

Use this only when you need to copy your local dataset into a fresh Railway PostgreSQL database.

Full runbook: [DATA_MIGRATION_CHECKLIST.md](DATA_MIGRATION_CHECKLIST.md).

1. Commit and deploy `render_seed.json` once.
2. Set `SEED_DATA_ON_DEPLOY=True` in Railway variables.
3. Keep `SEED_FIXTURE_PATH=render_seed.json`.
4. Deploy once.
5. The command `python manage.py load_seed_once` will import only when:
	- Seeding is explicitly enabled.
	- The fixture file exists.
	- Product data is not already present.
6. After successful import:
	- Set `SEED_DATA_ON_DEPLOY=False`.
	- Remove `render_seed.json` from the repository.
	- Deploy again.

## Notes

- Uploaded media in local filesystem is not persistent on platform containers.
- For user-uploaded files/images, use external object storage (for example S3 or Cloudinary).