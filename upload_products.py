import os
import django

# Step 1: Read ALL products from LOCAL SQLite
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kulfi_config.settings')
django.setup()
from inventory.models import Product

local_products = list(Product.objects.values())
print(f"Found {len(local_products)} local products")

# Step 2: Switch to REMOTE database
from django.conf import settings
import dj_database_url
from django import db

REMOTE_URL = 'postgresql://kulfi_user:Sv3kaNqPJg4Oqco59sW7hilF5WclUm5c@dpg-d81nc48g4nts73883ang-a.oregon-postgres.render.com/kulfi_db_7yxh'
settings.DATABASES['default'] = dj_database_url.config(default=REMOTE_URL, conn_max_age=0, ssl_require=True)
db.connections.close_all()

# Step 3: Clear existing remote products and insert local ones
existing = Product.objects.count()
print(f"Remote currently has {existing} products. Clearing...")
Product.objects.all().delete()
print("Cleared remote products")

for p in local_products:
    p.pop('_state', None)
    name = p['name']
    sku = p['sku']
    Product.objects.create(**p)
    print(f"  Created: {name} (SKU: {sku})")

total = Product.objects.count()
print(f"\nSUCCESS! {total} products are now live on the website!")
