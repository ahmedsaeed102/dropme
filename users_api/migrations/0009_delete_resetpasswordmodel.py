# Generated by Django 4.1.7 on 2023-03-11 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users_api", "0008_alter_usermodel_address"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ResetPasswordModel",
        ),
    ]