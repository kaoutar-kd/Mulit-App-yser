# Generated by Django 5.0.2 on 2024-03-04 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_remove_image_title_image_image_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(max_length=50),
        ),
        migrations.DeleteModel(
            name='Role',
        ),
    ]
