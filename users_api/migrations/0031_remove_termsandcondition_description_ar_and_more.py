# Generated by Django 4.1.7 on 2024-10-27 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users_api', '0030_termsandcondition_about_app_ar_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='termsandcondition',
            name='description_ar',
        ),
        migrations.RemoveField(
            model_name='termsandcondition',
            name='description_en',
        ),
        migrations.RemoveField(
            model_name='termsandcondition',
            name='title_ar',
        ),
        migrations.RemoveField(
            model_name='termsandcondition',
            name='title_en',
        ),
    ]
