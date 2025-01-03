from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from PIL import Image

from utils import custom_upload_path
from car.constants import *

User = get_user_model()


class CarCategory(models.Model):
    title = models.CharField(_('Название'), max_length=100)
    icon = models.ImageField(
        _('Иконка'), upload_to=custom_upload_path, null=True
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Категория авто')
        verbose_name_plural = _('Категории авто')
        ordering = ('my_order',)


class CarBrand(models.Model):
    title = models.CharField(_('Название'), max_length=100)
    logo = models.ImageField(_('Логотип'), upload_to=custom_upload_path)
    category = models.ManyToManyField(
        CarCategory, verbose_name=_('Категория авто'),
        related_name='car_brands'
    )
    # f_category = models.ForeignKey(CarCategory, on_delete=models.SET_NULL, related_name='f_car_brands', null=True)
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Марка автомобиля')
        verbose_name_plural = _('Марки автомобиля')
        ordering = ('my_order',)


class CarModel(models.Model):
    title = models.CharField(_('Название'), max_length=100)
    category = models.ForeignKey(
        CarCategory, verbose_name=_('Категория авто'),
        on_delete=models.PROTECT, related_name='car_models'
    )
    brand = models.ForeignKey(
        CarBrand, verbose_name=_('Марка автомобиля'),
        on_delete=models.PROTECT, related_name='car_models'
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return f'{self.brand} - {self.title}'

    class Meta:
        verbose_name = _('Модель')
        verbose_name_plural = _('Модели')
        ordering = ('my_order',)


class CarBody(models.Model):
    title = models.CharField(_('Название'), max_length=100)
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Кузов')
        verbose_name_plural = _('Кузова')
        ordering = ('my_order',)


class CarDrive(models.Model):
    title = models.CharField(_('Название'), max_length=100)
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Привод')
        verbose_name_plural = _('Приводы')
        ordering = ('my_order',)


class Car(models.Model):
    # Виды двигателя
    GASOLINE = 'gasoline'
    GAS = 'gas'
    GASOLINE_GAZ = 'gasoline/gas'
    DIESEL = 'diesel'
    HYBRID = 'hybrid'
    ELECTRIC = 'electric'

    engines = (
        (GASOLINE, _('Бензин')),
        (GAS, _('Газ')),
        (GASOLINE_GAZ, _('Бензин/газ')),
        (DIESEL, _('Дизель')),
        (HYBRID, _('Гибрид')),
        (ELECTRIC, _('Электро')),
    )

    # Виды КПП
    MANUAL = 'manual'
    AUTOMATIC = 'automatic'
    VARIATOR = 'variator'
    ROBOT = 'robot'

    transmissions = (
        (MANUAL, _('Механика')),
        (AUTOMATIC, _('Автомат')),
        (VARIATOR, _('Вариатор')),
        (ROBOT, _('Робот')),
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    image = models.ImageField(
        _('Фотография'), upload_to=custom_upload_path, blank=True, null=True,
    )
    year = models.PositiveSmallIntegerField(_('Год выпуска'))
    model = models.ForeignKey(
        CarModel, verbose_name=_('Модель'), on_delete=models.PROTECT,
        related_name='cars'
    )
    engine = models.CharField(
        verbose_name=_('Двигатель'), max_length=15, choices=engines
    )
    engine_displacement = models.DecimalField(
        _('Объем'), max_digits=3, decimal_places=1
    )
    mileage = models.PositiveIntegerField(_('Пробег'), blank=True, null=True)
    transmission = models.CharField(
        _('КПП'), max_length=15, choices=transmissions
    )
    drive = models.ForeignKey(
        CarDrive, verbose_name=_('Привод'), on_delete=models.PROTECT,
        related_name='cars', null=True
    )
    user = models.ForeignKey(
        User, verbose_name=_('Владелец'), on_delete=models.CASCADE,
        related_name='cars'
    )
    body = models.ForeignKey(
        CarBody, verbose_name=_('Кузов'), on_delete=models.PROTECT,
        related_name='cars', null=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            default_size = 800
            width, height = img.size
            compress_count = width / default_size
            img = img.resize(
                (int(img.size[0] / compress_count),
                 int(img.size[1] / compress_count)),
                Image.Resampling.LANCZOS
            )
            img.save(self.image.path, quality=80, optimize=True)

    def __str__(self):
        return f'{self.user} - {self.model}'

    @property
    def get_title_for_purchase_request(self):
        if self.model and self.year:
            return f'{self.model} {self.year}'
        elif self.model and self.year and self.engine_displacement:
            return f'{self.model} {self.year} {self.engine_displacement}'
        else:
            return f'Нет данных'

    class Meta:
        verbose_name = _('Машины')
        verbose_name_plural = _('Машины')


class OilChange(models.Model):
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    oil_title = models.CharField(_('Название масла'), max_length=100)
    current_mileage = models.PositiveIntegerField(_('Текущий пробег'))
    next_replacement = models.PositiveIntegerField(_('Следующая замена'))
    change_date = models.DateField(_('Дата замены'))
    car = models.ForeignKey(
        Car, verbose_name=_('Машина'), on_delete=models.CASCADE,
        related_name='oil_changes'
    )

    class Meta:
        verbose_name = _('Замена масла')
        verbose_name_plural = _('Замены масла')


class Consumables(models.Model):
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    title = models.CharField(_('Название запчасти'), max_length=100)
    price = models.DecimalField(_('Цена'), max_digits=10, decimal_places=2)
    car = models.ForeignKey(
        Car, verbose_name=_('Машина'), on_delete=models.CASCADE,
        related_name='consumables'
    )

    class Meta:
        verbose_name = _('Расходники')
        verbose_name_plural = _('Расходники')


class PartCategory(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    is_common_parts = models.BooleanField(
        verbose_name=_('Общие детали (Шины, диски и другие)'), default=False,
        help_text=_(
            'Сюда вы можете добавить те детали, которые будут отображаться '
            'у бизнесов без привязки к марке машины'
        )
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    def clean(self):
        common_parts_category = (
            PartCategory.objects.filter(is_common_parts=True).exists()
        )
        if self.is_common_parts and common_parts_category:
            raise ValidationError(
                {"is_common_parts": _("Уже есть категория с общими деталями")}
            )

    class Meta:
        verbose_name = _('Категория запчастей')
        verbose_name_plural = _('Категории запчастей')
        ordering = ['my_order', ]


class Part(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    category = models.ForeignKey(
        PartCategory, verbose_name=_('Категория'), on_delete=models.PROTECT,
        related_name='parts', null=True
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Запчасть')
        verbose_name_plural = _('Запчасти')
        ordering = ('my_order',)


class PartManufacturerCountry(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Страна производитель запчасти')
        verbose_name_plural = _('Страны производители запчасти')
        ordering = ('my_order',)
