# Generated by Django 4.1.6 on 2023-09-30 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("admin_site_database", "0003_department_teacher_teacherschedulecache"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="teacher",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscriptions",
                to="admin_site_database.teacher",
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscriptions",
                to="admin_site_database.group",
            ),
        ),
    ]
