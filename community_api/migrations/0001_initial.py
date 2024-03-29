# Generated by Django 4.1.7 on 2023-04-19 02:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(default='welcome channels', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MessagesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=4000)),
                ('message_dt', models.DateTimeField(auto_now_add=True)),
                ('img', models.ImageField(null=True, upload_to='dropme_img_chat')),
                ('video', models.FileField(null=True, upload_to='dropme_file_chat')),
                ('channel_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel', to='community_api.channelsmodel')),
                ('emoji', models.ManyToManyField(blank=True, related_name='blog_likes', to=settings.AUTH_USER_MODEL)),
                ('user_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
