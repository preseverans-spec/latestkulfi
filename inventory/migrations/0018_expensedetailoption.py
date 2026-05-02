from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_stockorder_stockorderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseDetailOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Expense Detail Option',
                'verbose_name_plural': 'Expense Detail Options',
                'ordering': ['name'],
            },
        ),
    ]
