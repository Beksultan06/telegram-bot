# Generated by Django 3.2 on 2024-02-13 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchase_request', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='offer',
            options={'ordering': ('-created_at',), 'verbose_name': 'Ответ на заявку', 'verbose_name_plural': 'Ответы на заявку'},
        ),
        migrations.AlterModelOptions(
            name='purchaserequest',
            options={'ordering': ('-created_at',), 'verbose_name': 'Заявка', 'verbose_name_plural': 'Заявки'},
        ),
    ]
