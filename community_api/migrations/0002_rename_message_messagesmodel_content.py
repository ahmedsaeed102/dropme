# Generated by Django 4.1.7 on 2023-04-24 15:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community_api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messagesmodel',
            old_name='message',
            new_name='content',
        ),
    ]