# Generated by Django 5.1.2 on 2024-11-08 20:00

from django.db import migrations

from labet.scheduler import create_schedule


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0007_add_user_data'),
        ('django_q', '0018_task_success_index'),  # this is ugly
        # ('django_q', get_last_migration('django_q')), # this should work but it doesn't
    ]

    operations = [
        migrations.RunPython(create_schedule),
    ]
