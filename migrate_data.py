"""
Migrate all data from local SQLite to remote PostgreSQL.
This script reads from the local DB and writes to the remote DB directly.
"""
import os
import sys
import json
import django

# Force local SQLite first for the dump
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kulfi_config.settings')
django.setup()

from django.core.management import call_command
from io import StringIO

print("Step 1: Dumping data from local SQLite...")
output = StringIO()
call_command(
    'dumpdata',
    '--exclude', 'auth.permission',
    '--exclude', 'contenttypes',
    '--exclude', 'sessions',
    '--indent', '2',
    stdout=output
)
data = output.getvalue()
print(f"  Dumped {len(data)} bytes of data")

# Write to file
with open('migration_dump.json', 'w', encoding='utf-8') as f:
    f.write(data)
print("  Saved to migration_dump.json")

# Now switch to remote DB
REMOTE_URL = "postgresql://kulfi_user:Sv3kaNqPJg4Oqco59sW7hilF5WclUm5c@dpg-d81nc48g4nts73883ang-a.oregon-postgres.render.com/kulfi_db_7yxh"
os.environ['DATABASE_URL'] = REMOTE_URL

# Re-setup Django with the new DB
from django.conf import settings
import dj_database_url
settings.DATABASES['default'] = dj_database_url.config(default=REMOTE_URL, conn_max_age=600, ssl_require=True)

# Close all existing connections
from django import db
db.connections.close_all()

print("\nStep 2: Flushing remote database...")
call_command('flush', '--no-input')
print("  Remote database flushed.")

print("\nStep 3: Loading data into remote PostgreSQL...")
call_command('loaddata', 'migration_dump.json')
print("\n  DATA MIGRATION COMPLETE!")
print("  All products, users, sales, and inventory data are now live!")
