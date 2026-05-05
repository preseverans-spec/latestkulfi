from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_stock_invoice'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StockInvoice',
        ),
    ]
