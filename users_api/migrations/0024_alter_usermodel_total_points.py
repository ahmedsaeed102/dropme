# Generated by Django 4.1.7 on 2023-09-03 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users_api", "0023_feedback"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usermodel",
            name="total_points",
            field=models.PositiveIntegerField(default=0),
        ),
    ]