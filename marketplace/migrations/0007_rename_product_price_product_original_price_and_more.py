# Generated by Django 4.1.7 on 2023-08-27 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0006_alter_category_img"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="product_price",
            new_name="original_price",
        ),
        migrations.AddField(
            model_name="product",
            name="price_after_discount",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
