# Generated by Django 4.1.7 on 2023-06-03 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("machine_api", "0017_alter_recyclelog_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recyclelog",
            name="bottles",
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name="recyclelog",
            name="cans",
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
