# Generated by Django 4.1.6 on 2024-02-28 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site_database', '0006_rename_if_forum_telegramchat_is_forum'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='departments',
            field=models.ManyToManyField(related_name='teachers_m2m', to='admin_site_database.department'),
        ),
    ]
