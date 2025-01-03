import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from business.models import Business
from car.models import Car, Part, PartManufacturerCountry, CarModel, CarBody, \
    CarDrive
from info.models import Region
from car.constants import *
from notification.models import Notification
from utils import custom_upload_path
from src.redis import red

User = get_user_model()


class PurchaseRequestType(models.Model):
    class Meta:
        verbose_name_plural = 'Тип заявок'
        verbose_name = 'Тип заявки'
        ordering = ['my_order']

    name = models.CharField(max_length=255, verbose_name='Название')
    text = models.TextField(max_length=60, verbose_name='Текст')
    cost = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Стоимость')
    icon = models.ImageField(upload_to=custom_upload_path, null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )


class PurchaseRequest(models.Model):
    type = models.ForeignKey(PurchaseRequestType, on_delete=models.SET_NULL, null=True, verbose_name='Тип заявки')
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    description = models.TextField(_('Описание'), null=True, blank=True)
    region = models.ForeignKey(
        Region, verbose_name=_('Регион'), on_delete=models.CASCADE,
        related_name='purchase_request', null=True
    )
    part = models.ForeignKey(
        Part, verbose_name=_('Запчасть'), on_delete=models.CASCADE,
        related_name='purchase_request', null=True
    )
    user = models.ForeignKey(
        User, verbose_name=_('Создатель заявки'), on_delete=models.CASCADE,
        related_name='purchase_request',
    )
    is_active = models.BooleanField(_('Активный'), default=True)

    viewed_users = models.ManyToManyField(User, blank=True)

    # CAR

    car_image = models.ImageField(
        _('Фотография'), upload_to=custom_upload_path, blank=True, null=True,
    )
    year = models.PositiveSmallIntegerField(_('Год выпуска'), null=True)
    model = models.ForeignKey(
        CarModel, verbose_name=_('Модель'), on_delete=models.CASCADE,
        related_name='purchase_request', null=True
    )
    engine = models.CharField(
        verbose_name=_('Двигатель'), max_length=15, choices=engines,
        blank=True, null=True,
    )
    engine_displacement = models.DecimalField(
        _('Объем'), max_digits=5, decimal_places=1, blank=True, null=True
    )
    mileage = models.PositiveIntegerField(_('Пробег'), blank=True, null=True)
    vin_code = models.CharField(max_length=17, null=True, blank=True, verbose_name='VIN код')
    transmission = models.CharField(
        _('КПП'), max_length=15, choices=transmissions, blank=True, null=True
    )
    drive = models.ForeignKey(
        CarDrive, verbose_name=_('Привод'), on_delete=models.CASCADE,
        related_name='purchase_request', null=True, blank=True
    )
    body = models.ForeignKey(
        CarBody, verbose_name=_('Кузов'), on_delete=models.CASCADE,
        related_name='purchase_request', null=True, blank=True
    )

    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')
        ordering = ('-created_at',)

    def __str__(self):
        return str(self.id)

    def deactivate(self):
        self.is_active = False
        self.save()

    def viewed_users_count(self):
        return self.viewed_users.count()

    def get_is_viewed_by_request_user(self, user):
        return True if self.viewed_users.filter(id=user.id).exists() else False

    @property
    def is_paid(self):
        return True if self.type.cost > 0 else False

    @property
    def get_title_for_purchase_request(self):
        if not self.model and not self.year:
            return f'Нет данных'
        title = f'{self.model} {self.year}'
        if self.engine_displacement:
            title += f' {self.engine_displacement}'
        return title

    @property
    def redis_not_viewed_offers_key(self):
        return f'purchase_request:{self.pk};offers:'

    def get_new_offers_count(self):
        key = f'{self.redis_not_viewed_offers_key}*'
        new_offers_keys = red.keys(key)
        return len(new_offers_keys)

    def view_new_offers(self):
        key = f'{self.redis_not_viewed_offers_key}*'
        new_offers_keys = red.keys(key)
        if new_offers_keys:
            red.delete(*new_offers_keys)

    @property
    def redis_not_viewed_messages_key(self):
        return f'purchase_request:{self.pk};messages:'

    def get_new_messages_count(self):
        key = f'{self.redis_not_viewed_messages_key}*'
        new_offers_keys = red.keys(key)
        return len(new_offers_keys)

    def view_new_messages(self):
        key = f'{self.redis_not_viewed_messages_key}*'
        new_messages_keys = red.keys(key)
        if new_messages_keys:
            red.delete(*new_messages_keys)

    def has_offers_from_this_business(self, business):
        return self.offers.filter(business=business).exists()


class PurchaseRequestImage(models.Model):
    image = models.ImageField(_('Изображение'), upload_to=custom_upload_path)
    purchase_request = models.ForeignKey(
        PurchaseRequest, verbose_name=_('Заявка'), on_delete=models.CASCADE,
        related_name='images'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
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

    class Meta:
        verbose_name = _('Изображение для заявки')
        verbose_name_plural = _('Изображения для заявки')


class Offer(models.Model):
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

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    part_manufacturer_country = models.ForeignKey(
        PartManufacturerCountry, verbose_name=_('Страна производитель'),
        on_delete=models.PROTECT, related_name='offers',
        null=True, blank=True
    )
    condition_of_part = models.CharField(
        _('Состояние запчасти'), max_length=20, choices=CONDITIONS, null=True, blank=True
    )
    difference = models.CharField(
        _('Отличие'), max_length=20, choices=DIFFERENCES, null=True, blank=True
    )
    price = models.DecimalField(_('Цена'), max_digits=10, decimal_places=2)
    comment = models.TextField(_('Комментарий'), null=True, blank=True)
    purchase_request = models.ForeignKey(
        PurchaseRequest, verbose_name=_('Заявка'), on_delete=models.CASCADE,
        related_name='offers',
    )
    business = models.ForeignKey(
        Business, verbose_name=_('Бизнес'), on_delete=models.CASCADE,
        related_name='offers',
    )
    availability = models.CharField(
        _('Наличие'), max_length=20, choices=AVAILABILITIES, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Ответ на заявку'
        verbose_name_plural = 'Ответы на заявку'
        ordering = ('-created_at',)

    def create_redis_not_viewed_key(self):
        key = f'{self.purchase_request.redis_not_viewed_offers_key}:{self.pk}'
        red.set(key, 1)

    def create_offer_notification(self):
        notification = Notification.objects.create(
            offer=self, message=Notification.purchase_request_message,
        )
        notification.users.add(self.purchase_request.user)
        notification.create_redis_view()

    def accept_offer_notification(self):
        notification = Notification.objects.create(
            offer=self, message=Notification.offer_message,
        )
        notification.users.add(self.business.user)
        notification.create_redis_view()
        notification.send()


class OfferImage(models.Model):
    image = models.ImageField(_('Изображение'), upload_to=custom_upload_path)
    offer = models.ForeignKey(
        Offer, verbose_name=_('Ответ на заявку'),
        on_delete=models.CASCADE, related_name='images'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
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

    class Meta:
        verbose_name = _('Изображение для ответа на заявку')
        verbose_name_plural = _('Изображения для ответа на заявку')
