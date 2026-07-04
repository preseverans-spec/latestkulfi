from django.db import migrations, models
import django.db.models.deletion


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
        manufacturer, _ = Manufacturer.objects.get_or_create(
            name=clean_name,
            defaults={'code': PREFIX_BY_NAME.get(clean_name.lower(), ''), 'description': ''},
        )
        if not manufacturer.code:
            manufacturer.code = PREFIX_BY_NAME.get(clean_name.lower(), '')
            manufacturer.save(update_fields=['code'])
        manufacturer_map[clean_name] = manufacturer

    for product in Product.objects.all():
        clean_category = (product.category or '').strip()
        if not clean_category:
            continue
        manufacturer = manufacturer_map.get(clean_category)
        if manufacturer and product.manufacturer_id != manufacturer.id:
            product.manufacturer_id = manufacturer.id
            product.save(update_fields=['manufacturer'])


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_delete_authlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('code', models.CharField(blank=True, default='', max_length=20)),
                ('description', models.TextField(blank=True, default='')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='inventory.manufacturer'),
        ),
        migrations.RunPython(forwards, backwards),
    ]