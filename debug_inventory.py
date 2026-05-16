#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kulfi_config.settings')
django.setup()

from inventory.models import Product, Sales
from datetime import date

print('=== Sales on March 29, 2026 ===')
sales_29 = Sales.objects.filter(sale_date=date(2026, 3, 29))
print(f'Count: {sales_29.count()}')
total_29 = 0
for sale in sales_29:
    print(f'  - {sale.product.name}: {sale.quantity} units (SKU: {sale.product.sku})')
    total_29 += sale.quantity
print(f'Total quantity sold on 29th: {total_29}')

print()
print('=== Sales on March 30, 2026 ===')
sales_30 = Sales.objects.filter(sale_date=date(2026, 3, 30))
print(f'Count: {sales_30.count()}')
total_30 = 0
for sale in sales_30:
    print(f'  - {sale.product.name}: {sale.quantity} units (SKU: {sale.product.sku})')
    total_30 += sale.quantity
print(f'Total quantity sold on 30th: {total_30}')

print()
print('=== All Products Stock Status ===')
products = Product.objects.all()
for p in products:
    print(f'{p.name} (SKU: {p.sku}): {p.current_stock} units')

print()
print('=== Stock Analysis (assuming starting stock on 28th was 444) ===')
# Calculate what the stock should be
all_sales = Sales.objects.filter(sale_date__in=[date(2026, 3, 29), date(2026, 3, 30)])
all_sales_count = all_sales.count()
all_sales_qty = sum(s.quantity for s in all_sales)

print(f'Total sales recorded: {all_sales_count} transactions')
print(f'Total quantity sold: {all_sales_qty} units')
print(f'Expected stock (444 - {all_sales_qty}): {444 - all_sales_qty}')
