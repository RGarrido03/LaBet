# Generated by Django 5.1.2 on 2024-10-24 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_alter_bethouse_logo_alter_team_logo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tier",
            name="description",
        ),
        migrations.AddField(
            model_name="tier",
            name="charts_included",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="tier",
            name="max_bets",
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name="tier",
            name="max_wallet",
            field=models.DecimalField(decimal_places=2, default=10, max_digits=10),
        ),
        migrations.AddField(
            model_name="tier",
            name="min_arbitrage",
            field=models.DecimalField(decimal_places=2, default=0.95, max_digits=10),
        ),
        migrations.AddField(
            model_name="tier",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
