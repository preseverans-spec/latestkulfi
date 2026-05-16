#!/usr/bin/env python
"""
Script to manually add missing sales records for March 29, 2026
This script creates Sales records and adjusts inventory accordingly
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kulfi_config.settings')
django.setup()

from inventory.models import Product, Sales
from datetime import date
from django.contrib.auth.models import User

# Get the system admin user (first staff user)
admin_user = User.objects.filter(is_staff=True).first()
if not admin_user:
    print("ERROR: No staff user found. Please create an admin user first.")
    exit(1)

print("=== Adding Missing March 29, 2026 Sales ===\n")

# Example: You need to fill in YOUR actual sales data here
# Format: (product_name, quantity_sold)
march_29_sales = [
    # Replace these with YOUR actual sales from March 29th
    # Example:
    # ('KC Malai', 20),
    # ('KC Kesar Badam', 15),
    # ... etc
]

print("INSTRUCTIONS:")
print("1. Edit this script and fill in the march_29_sales list")
print("2. Use format: ('Product Name', quantity)")
print("3. Product names must exactly match database")
print()

# Get all products for reference
print("Available products in system:")
products = Product.objects.all().order_by('sku')
for p in products:
    print(f"  - {p.name} (SKU: {p.sku}, Current Stock: {p.current_stock})")

print()

if not march_29_sales:
    print("No sales data provided. Please edit march_29_sales list and re-run.")
    print()
    print("Example:")
    print("march_29_sales = [")
    print("    ('KC Malai', 50),")
    print("    ('KC Kesar Badam', 30),")
    print("    ('KC Strawberry', 20),")
    print("]")
    exit(1)

# Check stock before adding
total_qty = 0
for product_name, quantity in march_29_sales:
    try:
        product = Product.objects.get(name=product_name)
        total_qty += quantity
        print(f"✓ {product_name}: {quantity} units", end="")
        if quantity > product.current_stock:
            print(f" (⚠ WARNING: Only {product.current_stock} units available)")
        else:
            print()
    except Product.DoesNotExist:
        print(f"✗ {product_name}: Product not found!")

print(f"\nTotal quantity: {total_qty} units")
print()

# Ask for confirmation
confirm = input("Proceed with adding these sales for March 29, 2026? (yes/no): ")
if confirm.lower() != 'yes':
    print("Cancelled.")
    exit(0)

# Add the sales
added = 0
for product_name, quantity in march_29_sales:
    try:
        product = Product.objects.get(name=product_name)
        
        # Create the sale record
        sale = Sales.objects.create(
            product=product,
            quantity=quantity,
            unit_price=product.selling_price,
            sale_date=date(2026, 3, 29),
            recorded_by=admin_user
        )
        
        # Reduce stock
        product.current_stock -= quantity
        product.save()
        
        print(f"✓ Added: {product.name} - {quantity} units")
        added += 1
        
    except Product.DoesNotExist:
        print(f"✗ Skipped: {product_name} not found")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

print()
print(f"Successfully added {added} sales records")

# Show stock after update
print()
print("=== Updated Stock (Total Quantity All Products) ===")
total_stock = sum(p.current_stock for p in Product.objects.all())
print(f"Total stock across all products: {total_stock} units")
