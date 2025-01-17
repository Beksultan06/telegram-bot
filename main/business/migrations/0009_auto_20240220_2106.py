# Generated by Django 3.2 on 2024-02-20 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0008_auto_20240212_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='business_images/', verbose_name='Фотография'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Сумма'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='business.business', verbose_name='Бизнес'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.TextField(default='', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='success',
            field=models.BooleanField(default=False, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type_of_transaction',
            field=models.CharField(choices=[('deposit', 'Пополнение'), ('withdrawal', 'Снятие')], max_length=10, verbose_name='Тип'),
        ),
    ]
