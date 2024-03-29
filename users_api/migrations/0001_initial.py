# Generated by Django 4.1.7 on 2023-04-23 11:46

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import users_api.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="LocationModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("address", models.CharField(default="Egypt", max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="UserModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("username", models.CharField(max_length=50)),
                (
                    "email",
                    models.EmailField(
                        max_length=50,
                        unique=True,
                        validators=[django.core.validators.EmailValidator()],
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=11,
                        null=True,
                        unique=True,
                        validators=[users_api.models.validate_phone_number],
                    ),
                ),
                ("otp", models.CharField(max_length=4)),
                ("otp_expiration", models.DateTimeField(blank=True, null=True)),
                ("max_otp_try", models.CharField(default=3, max_length=2)),
                ("max_otp_out", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=False)),
                ("is_staff", models.BooleanField(default=False)),
                ("registered_at", models.DateTimeField(auto_now_add=True)),
                (
                    "profile_photo",
                    models.ImageField(
                        default="upload_to/default.png", upload_to="upload_to"
                    ),
                ),
                ("age", models.IntegerField(null=True)),
                (
                    "gender",
                    models.CharField(
                        choices=[("male", "male"), ("female", "female")],
                        default="male",
                        max_length=20,
                    ),
                ),
                (
                    "total_points",
                    models.PositiveIntegerField(
                        default=0, help_text="User total earned points"
                    ),
                ),
                (
                    "address",
                    models.ForeignKey(
                        default=1,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="address_name",
                        to="users_api.locationmodel",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ("-total_points",),
            },
        ),
    ]
