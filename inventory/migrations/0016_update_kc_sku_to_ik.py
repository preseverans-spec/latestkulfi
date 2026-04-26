from django.db import migrations


def forwards_func(apps, schema_editor):
    Product = apps.get_model('inventory', 'Product')
    for product in Product.objects.filter(sku__startswith='KC0'):
        product.sku = product.sku.replace('KC', 'IK', 1)
        product.save(update_fields=['sku'])


def backwards_func(apps, schema_editor):
    Product = apps.get_model('inventory', 'Product')
    for product in Product.objects.filter(sku__startswith='IK0'):
        product.sku = product.sku.replace('IK', 'KC', 1)
        product.save(update_fields=['sku'])


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0015_salescountdraft_delete_salesstockbalance'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
