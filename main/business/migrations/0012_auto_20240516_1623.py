# Generated by Django 3.2 on 2024-05-16 10:23

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0011_auto_20240407_0001'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='business',
            options={'verbose_name': 'Бизнес аккаунт', 'verbose_name_plural': 'Бизнес аккаунты'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ('my_order',), 'verbose_name': 'Магазин', 'verbose_name_plural': 'Магазины'},
        ),
        migrations.AlterModelOptions(
            name='servicesubcategory',
            options={'ordering': ('my_order',), 'verbose_name': 'Подкатегория магазина', 'verbose_name_plural': 'Подкатегории магазинов'},
        ),
        migrations.AlterField(
            model_name='service',
            name='image',
            field=models.ImageField(null=True, upload_to=utils.custom_upload_path, verbose_name='Фотография'),
        ),
    ]
