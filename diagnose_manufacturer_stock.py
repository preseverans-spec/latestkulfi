"""
Read-only diagnostic script for the Manufacturer/stock-merge investigation.
Does NOT print or log any credentials.

Usage (run this yourself, do not share your DATABASE_URL with anyone):
    $env:DATABASE_URL="<your Render External Database URL>"
    .\.venv\Scripts\python.exe manage.py shell < diagnose_manufacturer_stock.py
or:
    .\.venv\Scripts\python.exe manage.py runscript diagnose_manufacturer_stock  (if django-extensions is installed)

Simplest: paste the contents of the "CODE" block below directly into:
    .\.venv\Scripts\python.exe manage.py shell
"""

from inventory.models import Manufacturer, Product, Sales, Inventory
import datetime

TODAY = datetime.date(2026, 9, 18)

print('=== Manufacturers ===')
for m in Manufacturer.objects.all():
    print(m.id, repr(m.name), m.code, m.is_active)

print()
print('=== Malai variants (id, manufacturer, current_stock) ===')
for p in Product.objects.filter(name__iexact='Malai', is_active=True).select_related('manufacturer'):
    print(p.id, p.name, '|', p.manufacturer.name if p.manufacturer else None, '| stock=', p.current_stock)

print()
print('=== Inventory movements today for Malai ===')
for mv in Inventory.objects.filter(product__name__iexact='Malai', movement_date=TODAY).select_related('product', 'product__manufacturer').order_by('created_at'):
    print(mv.id, mv.product.name, '|', mv.product.manufacturer.name if mv.product.manufacturer else None,
          '| type=', mv.movement_type, '| qty=', mv.quantity, '| notes=', mv.notes, '| created_at=', mv.created_at)

print()
print('=== Sales today for Malai ===')
for s in Sales.objects.filter(product__name__iexact='Malai', sale_date=TODAY).select_related('product', 'product__manufacturer').order_by('created_at'):
    print(s.id, s.product.name, '|', s.product.manufacturer.name if s.product.manufacturer else None,
          '| qty=', s.quantity, '| recorded_by=', s.recorded_by, '| created_at=', s.created_at)
