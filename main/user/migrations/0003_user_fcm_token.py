# Generated by Django 3.2 on 2024-01-06 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20231120_0054'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Firebase токен'),
        ),
    ]
