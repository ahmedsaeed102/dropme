# Generated by Django 4.1.7 on 2023-04-08 11:37

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "machine_api",
            "0011_remove_machine_latitdue_remove_machine_longitude_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="machine",
            name="location",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
    ]