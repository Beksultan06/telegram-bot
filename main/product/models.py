from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from business.models import Business, Service
from car.models import CarModel, CarBrand, CarCategory, PartCategory, Part, PartManufacturerCountry


# Create your models here.

class Product(models.Model):
    USED = 'used'
    NEW = 'new'
    CONDITIONS = (
        (NEW, 'Новый'),
        (USED, 'Б/У'),
    )
    IN_STOCK = 'in_stock'
    TO_ORDER = 'to_order'
    AVAILABILITIES = (
        (IN_STOCK, 'В наличии'),
        (TO_ORDER, 'Под заказ'),
    )
    ORIGINAL = 'original'
    ANALOGUE = 'analogue'
    DIFFERENCES = (
        (ORIGINAL, 'Оригинал'),
        (ANALOGUE, 'Аналог'),
    )

    title = models.CharField(_('Название'), max_length=200)
    description = models.TextField(_('Описание'), blank=True, null=True)
    price = models.DecimalField(_('Цена'), max_digits=10, decimal_places=2)
    car_model = models.ForeignKey(
        CarModel, verbose_name=_('Модель автомобиля'), on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    car_brand = models.ForeignKey(
        CarBrand, verbose_name=_('Марка автомобиля'), on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    car_category = models.ForeignKey(
        CarCategory, verbose_name=_('Категория автомобиля'), on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    part = models.ForeignKey(
        Part, verbose_name=_('Запчасть'), on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    manufacturer_country = models.ForeignKey(
        PartManufacturerCountry, verbose_name=_('Страна производителя запчасти'), on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    year = models.PositiveSmallIntegerField(_('Год выпуска'), null=True, blank=True)
    shop = models.ForeignKey(Service, verbose_name=_('Магазин'), on_delete=models.SET_NULL, related_name='products',
                             null=True, blank=True)
    shop_price = models.DecimalField(_('Цена на магазине'), max_digits=10, decimal_places=2, null=True, blank=True)

    condition_of_part = models.CharField(
        _('Состояние запчасти'), max_length=20, choices=CONDITIONS, null=True, blank=True
    )
    difference = models.CharField(
        _('Отличие'), max_length=20, choices=DIFFERENCES, null=True, blank=True
    )
    availability = models.CharField(
        _('Наличие'), max_length=20, choices=AVAILABILITIES, null=True, blank=True
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        ordering = ('created_at',)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Товар'), on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('Изображение'), upload_to='product_images/')
    is_main = models.BooleanField(_('Основное изображение'), default=False)

    class Meta:
        verbose_name = _('Изображение товара')
        verbose_name_plural = _('Изображения товара')
        ordering = ('product',)
