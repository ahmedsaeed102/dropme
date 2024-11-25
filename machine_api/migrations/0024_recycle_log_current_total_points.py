from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('machine_api', '0023_recycle_log_machine'),
    ]

    operations = [
        migrations.AddField(
            model_name='recyclelog',
            name='current_total_points',
            field=models.IntegerField(default=0),
        ),
    ]