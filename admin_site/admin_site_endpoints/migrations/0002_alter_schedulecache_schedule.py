# Generated by Django 4.1.6 on 2023-07-30 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site_endpoints', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulecache',
            name='schedule',
            field=models.JSONField(null=True),
        ),
    ]
