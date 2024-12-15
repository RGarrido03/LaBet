# Generated by Django 5.1.3 on 2024-12-15 02:07

import app.utils.date
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_add_scheduler'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='birth_date',
            field=models.DateField(null=True, validators=[app.utils.date.validate_age]),
        ),
    ]
