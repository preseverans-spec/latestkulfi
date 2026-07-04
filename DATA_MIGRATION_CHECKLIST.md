# Data Migration Checklist (Local -> Render/Railway)

Use this checklist when you want production data to match your local PostgreSQL data.

## A) Pre-checks

1. Confirm local app is using PostgreSQL (not SQLite).
2. Confirm local DB has the data you want to publish.
3. Confirm target cloud DB is fresh, or decide if you will replace existing data.

## B) Create export from local PostgreSQL

Run from project root:

```powershell
$env:DATABASE_URL='postgresql://postgres@localhost:5433/kulfi_local'
& "c:/Users/DELL/Desktop/latestkulfi-main/.venv/Scripts/python.exe" manage.py dumpdata --exclude auth.permission --exclude contenttypes --exclude sessions --natural-foreign --natural-primary --indent 2 --output render_seed.json
```

Optional validation:

```powershell
& "c:/Users/DELL/Desktop/latestkulfi-main/.venv/Scripts/python.exe" -c "import json; d=json.load(open('render_seed.json', encoding='utf-8')); print('objects', len(d))"
```

## C) Prepare deployment

1. Commit code changes needed for deployment.
2. Commit render_seed.json only for one deployment.
3. Push to GitHub.

## D) Enable one-time seed in platform variables

Set these in Render or Railway:

- SEED_DATA_ON_DEPLOY=True
- SEED_FIXTURE_PATH=render_seed.json

Keep normal required variables as-is:

- DATABASE_URL
- SECRET_KEY
- ALLOWED_HOSTS
- CSRF_TRUSTED_ORIGINS
- ADMIN_USERNAME
- ADMIN_EMAIL
- ADMIN_PASSWORD

## E) Deploy and import

1. Trigger deployment.
2. Build runs migrations and then load_seed_once.
3. Seed import occurs only if all are true:
   - SEED_DATA_ON_DEPLOY is enabled.
   - Fixture file exists.
   - Product table is empty.

## F) Verify after deploy

Run in platform shell:

```bash
python manage.py shell -c "from inventory.models import Product; from django.contrib.auth import get_user_model; U=get_user_model(); print('products', Product.objects.count()); print('users', U.objects.count())"
```

Check app pages:

1. Login page loads.
2. Admin panel works.
3. Product list and key reports show expected records.

## G) Cleanup (important)

1. Set SEED_DATA_ON_DEPLOY=False.
2. Remove render_seed.json from the repository.
3. Push and deploy again.

This prevents accidental re-import and avoids keeping business/user data in Git.

## H) If you must replace existing production data

Run in platform shell before seed:

```bash
python manage.py flush --no-input
```

Then redeploy with SEED_DATA_ON_DEPLOY=True, verify, and perform cleanup in section G.
