# Generated by Django 4.1.7 on 2023-04-08 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("machine_api", "0012_alter_machine_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="machine",
            name="status_ar",
            field=models.CharField(
                choices=[("available", "متاح"), ("breakdown", "لا تعمل")],
                default="available",
                max_length=20,
            ),
        ),
    ]
