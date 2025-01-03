# Generated by Django 3.2 on 2024-02-06 16:55

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0003_auto_20240131_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='drive',
            field=models.CharField(choices=[('front_wheel', 'Передний привод'), ('rear_wheel', 'Задний привод'), ('four_wheel', 'Полный привод')], max_length=15, verbose_name='Привод'),
        ),
        migrations.AlterField(
            model_name='car',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=utils.custom_upload_path, verbose_name='Фотография'),
        ),
    ]
