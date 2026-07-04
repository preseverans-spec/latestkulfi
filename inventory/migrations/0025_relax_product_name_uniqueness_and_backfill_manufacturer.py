from django.db import migrations, models


PREFIX_BY_NAME = {
    'indian kulfi': 'IK',
    'kulfi corner': 'KC',
    'new bowring': 'NB',
}


def forwards(apps, schema_editor):
    Manufacturer = apps.get_model('inventory', 'Manufacturer')
    Product = apps.get_model('inventory', 'Product')

    category_values = set(
        Product.objects.exclude(category__isnull=True)
        .exclude(category__exact='')
        .values_list('category', flat=True)
    )

    manufacturer_map = {}
    for category in category_values:
        clean_name = (category or '').strip()
        if not clean_name:
            continue

        existing = Manufacturer.objects.filter(name__iexact=clean_name).first()
        if existing:
            manufacturer = existing
            if not manufacturer.code:
                manufacturer.code = PREFIX_BY_NAME.get(clean_name.lower(), '')
                manufacturer.save(update_fields=['code'])
        else:
            manufacturer = Manufacturer.objects.create(
                name=clean_name,
                code=PREFIX_BY_NAME.get(clean_name.lower(), ''),
                description='',
            )

        manufacturer_map[clean_name.lower()] = manufacturer

    for product in Product.objects.all():
        clean_category = (product.category or '').strip()
        if not clean_category:
            continue

        manufacturer = manufacturer_map.get(clean_category.lower())
        if manufacturer and product.manufacturer_id != manufacturer.id:
            product.manufacturer_id = manufacturer.id
            product.save(update_fields=['manufacturer'])


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_merge_20260703_0001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.RunPython(forwards, backwards),
    ]
