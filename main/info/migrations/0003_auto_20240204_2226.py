# Generated by Django 3.2 on 2024-02-04 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0002_auto_20240112_2245'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'verbose_name': 'Акция от партнера', 'verbose_name_plural': 'Акции от партнера'},
        ),
        migrations.RemoveField(
            model_name='banner',
            name='my_order',
        ),
    ]
