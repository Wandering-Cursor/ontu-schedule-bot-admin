# Generated by Django 4.2.19 on 2025-03-05 17:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("admin_site_database", "0007_teacher_departments"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="group",
            options={"ordering": ["faculty", "name", "-created"]},
        ),
    ]
