# Generated by Django 4.1.7 on 2023-04-08 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("machine_api", "0010_alter_machine_latitdue"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="machine",
            name="latitdue",
        ),
        migrations.RemoveField(
            model_name="machine",
            name="longitude",
        ),
        migrations.AddField(
            model_name="machine",
            name="city_ar",
            field=models.CharField(
                blank=True,
                help_text="arabic translation for Machine city",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="machine",
            name="name_ar",
            field=models.CharField(
                blank=True, help_text="arabic machine name", max_length=200, null=True
            ),
        ),
        migrations.AddField(
            model_name="machine",
            name="place_ar",
            field=models.CharField(
                blank=True,
                help_text="arabic machine address inside city",
                max_length=200,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="machine",
            name="place",
            field=models.CharField(
                help_text="machine address inside city", max_length=200, null=True
            ),
        ),
    ]