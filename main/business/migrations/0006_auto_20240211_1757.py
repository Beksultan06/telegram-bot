# Generated by Django 3.2 on 2024-02-11 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_auto_20240211_1654'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payboxorder',
            name='error_message',
        ),
        migrations.AlterField(
            model_name='payboxorder',
            name='status',
            field=models.CharField(choices=[('processing', 'В обработке'), ('failed', 'Отклонено'), ('success', 'Успешно'), ('not_completed', 'Не завершен')], default='processing', max_length=20, verbose_name='Статус'),
        ),
    ]
