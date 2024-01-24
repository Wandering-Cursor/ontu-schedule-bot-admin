# Generated by Django 4.1.6 on 2023-09-23 13:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site_database', '0002_messagecampaign'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
                ('external_id', models.CharField(max_length=255, unique=True)),
                ('short_name', models.TextField()),
                ('full_name', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
                ('external_id', models.CharField(max_length=255, unique=True)),
                ('short_name', models.CharField(max_length=255)),
                ('full_name', models.TextField()),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='admin_site_database.department')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeacherScheduleCache',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
                ('expires_on', models.DateTimeField()),
                ('schedule', models.JSONField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule_cache', to='admin_site_database.teacher')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
