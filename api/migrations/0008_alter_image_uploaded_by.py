# Generated by Django 5.0.2 on 2024-03-04 22:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_role_alter_user_username_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='uploaded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
