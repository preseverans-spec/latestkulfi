from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_stock_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockinvoice',
            name='drive_file_id',
            field=models.CharField(blank=True, help_text='Google Drive file ID (optional)', max_length=255),
        ),
        migrations.AddField(
            model_name='stockinvoice',
            name='drive_mime_type',
            field=models.CharField(blank=True, help_text='Google Drive MIME type (optional)', max_length=120),
        ),
        migrations.AddField(
            model_name='stockinvoice',
            name='original_filename',
            field=models.CharField(blank=True, help_text='Original uploaded filename', max_length=255),
        ),
    ]
