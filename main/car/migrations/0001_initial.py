# Generated by Django 3.2 on 2024-01-11 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('image', models.ImageField(upload_to=utils.custom_upload_path, verbose_name='Фотография')),
                ('year', models.PositiveSmallIntegerField(verbose_name='Год выпуска')),
                ('engine', models.CharField(choices=[('gasoline', 'Бензин'), ('gas', 'Газ'), ('gasoline/gas', 'Бензин/газ'), ('diesel', 'Дизель'), ('hybrid', 'Гибрид'), ('electric', 'Электро')], max_length=15, verbose_name='Двигатель')),
                ('engine_displacement', models.DecimalField(decimal_places=1, max_digits=3, verbose_name='Объем')),
                ('mileage', models.PositiveIntegerField(verbose_name='Пробег')),
                ('transmission', models.CharField(choices=[('manual', 'Механика'), ('automatic', 'Автомат'), ('variator', 'Вариатор'), ('robot', 'Робот')], max_length=15, verbose_name='КПП')),
                ('drive', models.CharField(choices=[('front_wheel', 'Передний привод'), ('rear_wheel', 'Задний привод'), ('four_wheel', 'Полынй привод')], max_length=15, verbose_name='Привод')),
            ],
            options={
                'verbose_name': 'Машины',
                'verbose_name_plural': 'Машины',
            },
        ),
        migrations.CreateModel(
            name='CarBody',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Кузов',
                'verbose_name_plural': 'Кузова',
            },
        ),
        migrations.CreateModel(
            name='CarBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('logo', models.ImageField(upload_to=utils.custom_upload_path, verbose_name='Логотип')),
            ],
            options={
                'verbose_name': 'Марка автомобиля',
                'verbose_name_plural': 'Марки автомобиля',
            },
        ),
        migrations.CreateModel(
            name='CarCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Категория авто',
                'verbose_name_plural': 'Категории авто',
            },
        ),
        migrations.CreateModel(
            name='PartCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('is_common_parts', models.BooleanField(default=False, help_text='Сюда вы можете добавить те детали, которые будут отображаться у бизнесов без привязки к марке машины', verbose_name='Общие детали (Шины, диски и другие)')),
                ('my_order', models.PositiveIntegerField(default=0, verbose_name='Очередь')),
            ],
            options={
                'verbose_name': 'Категория запчастей',
                'verbose_name_plural': 'Категории запчастей',
                'ordering': ['my_order'],
            },
        ),
        migrations.CreateModel(
            name='PartManufacturerCountry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Страна производитель запчасти',
                'verbose_name_plural': 'Страны производители запчасти',
            },
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parts', to='car.partcategory', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Запчасть',
                'verbose_name_plural': 'Запчасти',
            },
        ),
        migrations.CreateModel(
            name='OilChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('oil_title', models.CharField(max_length=100, verbose_name='Название масла')),
                ('current_mileage', models.PositiveIntegerField(verbose_name='Текущий пробег')),
                ('next_replacement', models.PositiveIntegerField(verbose_name='Следующая замена')),
                ('change_date', models.DateField(verbose_name='Дата замены')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oil_changes', to='car.car', verbose_name='Машина')),
            ],
            options={
                'verbose_name': 'Замена масла',
                'verbose_name_plural': 'Замены масла',
            },
        ),
        migrations.CreateModel(
            name='Consumables',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('title', models.CharField(max_length=100, verbose_name='Название запчасти')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consumables', to='car.car', verbose_name='Машина')),
            ],
            options={
                'verbose_name': 'Расходники',
                'verbose_name_plural': 'Расходники',
            },
        ),
        migrations.CreateModel(
            name='CarModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_models', to='car.carbrand', verbose_name='Марка автомобиля')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_models', to='car.carcategory', verbose_name='Категория авто')),
            ],
            options={
                'verbose_name': 'Модель',
                'verbose_name_plural': 'Модели',
            },
        ),
        migrations.AddField(
            model_name='car',
            name='body',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cars', to='car.carbody', verbose_name='Кузов'),
        ),
        migrations.AddField(
            model_name='car',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cars', to='car.carmodel', verbose_name='Модель'),
        ),
        migrations.AddField(
            model_name='car',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cars', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
    ]
