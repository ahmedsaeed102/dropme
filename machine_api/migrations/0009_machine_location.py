# Generated by Django 4.1.7 on 2023-03-18 18:05

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("machine_api", "0008_remove_machine_location_machine_city_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="machine",
            name="location",
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
    ]
