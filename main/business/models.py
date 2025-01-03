import copy
import hashlib
import xmltodict

import redis
import requests
from dateutil.relativedelta import relativedelta
from dicttoxml import dicttoxml
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from multiselectfield import MultiSelectField

from business.utils import generate_random_string
from info.models import Region
from notification.models import Notification
from utils import custom_upload_path
from src.redis import red

User = get_user_model()


class Tariff(models.Model):
    title = models.CharField(_('Название'), max_length=100, unique=True)
    logo = models.ImageField(
        _('Логотип'), upload_to=custom_upload_path, null=True
    )
    price = models.DecimalField(_('Цена'), max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        _('Старая цена'), max_digits=10, decimal_places=2, null=True,
        blank=True
    )
    description = models.TextField(_('Описание'), null=True, blank=True)
    car_brands_count = models.PositiveSmallIntegerField(
        _('Количество марок автомобиля')
    )
    common_parts_count = models.PositiveSmallIntegerField(
        _('Количество общих деталей'),
    )
    my_order = models.PositiveIntegerField(
        default=0, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Тариф')
        verbose_name_plural = _('Тарифы')
        ordering = ('my_order',)


class Business(models.Model):
    class Meta:
        verbose_name = _('Бизнес аккаунт')
        verbose_name_plural = _('Бизнес аккаунты')

    by_common_parts = "by_common_parts"
    by_car_brands = "by_car_brands"
    all_requests = "all_requests"

    TYPES_OF_PURCHASE_REQUESTS = (
        (by_common_parts, _('По общим деталям')),
        (by_car_brands, _('По марке автомобилей')),
        (all_requests, _('Все заявки'))
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    title = models.CharField(_('Название'), max_length=200)
    address = models.CharField(_('Адрес'), max_length=100)
    image = models.ImageField(
        _('Фотография'), upload_to='business_images/', blank=True, null=True,
    )
    tariff = models.ForeignKey(
        Tariff, verbose_name=_("Тариф"), on_delete=models.PROTECT,
        null=True, blank=True, related_name='businesses'
    )
    telegram = models.CharField(
        _('Telegram'), max_length=100, null=True, blank=True)
    instagram = models.CharField(
        _('Instagram'), max_length=100, null=True, blank=True
    )
    tiktok = models.CharField(
        _('TikTok'), max_length=100, null=True, blank=True
    )
    whatsapp = models.CharField(
        _('WhatsApp'), max_length=20, null=True, blank=True
    )
    user = models.OneToOneField(
        User, verbose_name=_('Пользователь'), on_delete=models.CASCADE
    )
    car_brands = models.ManyToManyField(
        'car.CarBrand', verbose_name=_('Марки машин'),
        related_name='businesses', blank=True
    )
    first_phone_number = models.CharField(
        _('Первый рабочий номер'), max_length=30,
        help_text="+996XXXXXXXXX или +996312XXXXXX"
    )
    second_phone_number = models.CharField(
        _('Второй рабочий номер'), max_length=30, null=True, blank=True,
        help_text="+996XXXXXXXXX или +996312XXXXXX"
    )
    third_phone_number = models.CharField(
        _('Третий рабочий номер'), max_length=30, null=True, blank=True,
        help_text="+996XXXXXXXXX или +996312XXXXXX"
    )
    is_active = models.BooleanField(verbose_name=_('Активный'), default=True)
    common_parts = models.ManyToManyField(
        'car.Part', verbose_name=_('Общие запчасти'),
        related_name='businesses', blank=True
    )
    types_of_purchase_requests = models.CharField(
        verbose_name=_("Виды заявок"), max_length=50,
        choices=TYPES_OF_PURCHASE_REQUESTS, default=all_requests
    )
    balance = models.DecimalField(
        verbose_name=_("Баланс"), max_digits=20, decimal_places=2, default=0
    )
    tariff_end_day = models.DateField(
        verbose_name=_("День окончания тарифа"), null=True, blank=True
    )

    def __str__(self):
        return self.title

    @property
    def business_user_name(self):
        return self.user.name

    @property
    def is_tariff_selected(self):
        return True if self.tariff else False

    @property
    def is_car_brands_selected(self):
        return self.car_brands.exists() or self.common_parts.exists()


    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

    def set_standard_tariff(self):
        tariff, _ = Tariff.objects.get_or_create(
            title='Стандарт', defaults={
                "price": 0, 'car_brands_count': 1, 'common_parts_count': 1
            },
        )
        self.tariff = tariff
        self.save()
        self.refresh_from_db()
        self.update_car_brands_and_common_parts_by_tariff()

    def update_car_brands_and_common_parts_by_tariff(self):
        self.common_parts.set(
            self.common_parts.all()[:self.tariff.common_parts_count]
        )
        self.car_brands.set(
            self.car_brands.all()[:self.tariff.car_brands_count]
        )

    def set_tariff_end_day(self):
        if self.tariff.price != 0:
            today = timezone.localtime(timezone.now())
            self.tariff_end_day = today + relativedelta(months=1)
        else:
            self.tariff_end_day = None
        self.save()

    @classmethod
    def increase_balance(cls, business_id, amount):
        with transaction.atomic():
            # Получаем объект бизнеса с блокировкой до завершения транзакции
            business = cls.objects.select_for_update().get(id=business_id)

            # Обновляем баланс с помощью F()-выражения
            business.balance = F('balance') + amount
            business.save()
            business.refresh_from_db()
        return business

    @classmethod
    def decrease_balance(cls, business_id, amount):
        with transaction.atomic():
            # Получаем объект бизнеса с блокировкой до завершения транзакции
            business = cls.objects.select_for_update().get(id=business_id)
            if business.balance < amount:
                raise ValueError(_("Недостаточно средств на балансе"))

            # Обновляем баланс с помощью F()-выражения
            business.balance = F('balance') - amount
            business.save()
            business.refresh_from_db()
        return business

    def create_tariff_expiring_notification(self):
        title = _("Ваш тариф скоро закончится")
        message = _(
            f'Ваш тариф "{self.tariff.title}" закончится через 3 дня '
            f'({self.tariff_end_day.strftime("%d.%m.%Y")}). '
            f'Не забудьте пополнить баланс'
        )
        notification = Notification.objects.create(
            title=title, message=message, tariff=self.tariff
        )
        notification.users.add(self.user)
        notification.create_redis_view()
        notification.send()

    def create_tariff_update_notification(self):
        title = _("Ваш тариф обновлён")
        message = _(
            f'Ваш тариф обновлен. Ваш текущий тариф - "{self.tariff.title}". '
            f'Ваш текущий баланс - "{self.balance}'
        )
        notification = Notification.objects.create(
            title=title, message=message, tariff=self.tariff
        )
        notification.users.add(self.user)
        notification.create_redis_view()
        notification.send()


class ServiceCategory(models.Model):
    title = models.CharField(_('Название'), max_length=100, db_index=True)
    image = models.ImageField(
        _('Изображение'), upload_to=custom_upload_path
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    @property
    def has_sub_categories(self):
        return self.sub_categories.exists()

    class Meta:
        verbose_name = _('Категория магазина')
        verbose_name_plural = _('Категории магазинов')
        ordering = ('my_order',)


class ServiceSubCategory(models.Model):
    title = models.CharField(_('Название'), max_length=100, db_index=True)
    category = models.ForeignKey(
        ServiceCategory, verbose_name=_('Категория'),
        on_delete=models.PROTECT, null=True, related_name='sub_categories'
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Подкатегория магазина')
        verbose_name_plural = _('Подкатегории магазинов')
        ordering = ('my_order',)


class Service(models.Model):
    class Meta:
        verbose_name = _('Магазин')
        verbose_name_plural = _('Магазины')
        ordering = ('my_order',)

    DAY_CHOICES = (
        (1, _('Понедельник')),
        (2, _('Вторник')),
        (3, _('Среда')),
        (4, _('Четверг')),
        (5, _('Пятница')),
        (6, _('Суббота')),
        (7, _('Воскресенье')),
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    title = models.CharField(_('Название'), max_length=200, db_index=True)
    address = models.CharField(_('Адрес'), max_length=100)
    comment = models.TextField(_('Комментарий'), default="")
    work_days = MultiSelectField(
        _('Рабочие дни'), choices=DAY_CHOICES, max_choices=7,
    )
    image = models.ImageField(
        _('Фотография'), upload_to=custom_upload_path, null=True
    )
    start_time = models.TimeField(_('Время начала работы'))
    end_time = models.TimeField(_('Время конца работы'))
    business = models.ForeignKey(
        Business, verbose_name=_('Бизнес'), on_delete=models.CASCADE,
        related_name='services'
    )
    categories = models.ManyToManyField(ServiceCategory, verbose_name='Категории магазинов')
    category = models.ForeignKey(
        ServiceCategory, verbose_name=_('Категория сервиса'),
        on_delete=models.PROTECT, null=True, related_name='services'
    )
    sub_category = models.ForeignKey(
        ServiceSubCategory, verbose_name=_('Подкатегория сервиса'),
        on_delete=models.PROTECT, null=True, blank=True,
        related_name='services', help_text=_(
            'Если выбрана подкатегория, то сервис будет отображаться только '
            'в подкатегории. В категории сервиса она отображаться не будет'
        )
    )
    region = models.ManyToManyField(
        Region, verbose_name=_('Регион'), related_name='services',
    )
    telegram = models.CharField(
        _('Telegram'), max_length=100, null=True, blank=True)
    instagram = models.CharField(
        _('Instagram'), max_length=100, null=True, blank=True
    )
    tiktok = models.CharField(
        _('TikTok'), max_length=100, null=True, blank=True
    )
    whatsapp = models.CharField(
        _('WhatsApp'), max_length=20, null=True, blank=True
    )
    first_phone_number = models.CharField(
        _('Первый рабочий номер'), max_length=30,
        help_text="+996XXXXXXXXX или +996312XXXXXX"
    )
    second_phone_number = models.CharField(
        _('Второй рабочий номер'), max_length=30, null=True, blank=True,
        help_text="+996XXXXXXXXX или +996312XXXXXX"
    )
    third_phone_number = models.CharField(
        _('Третий рабочий номер'), max_length=30, null=True, blank=True,
        help_text="+996XXXXXXXXX или +996312XXXXXX"
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    def get_image(self):
        return self.image.url if self.image \
            else 'https://as2.ftcdn.net/v2/jpg/07/86/72/89/1000_F_786728988_QyuP5WkUfZMlGMEMltILI72HWVtkEyYx.jpg'


class ServiceViewLog(models.Model):
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True,
                                 verbose_name='категория сервиса')
    service = models.ForeignKey(
        Service, verbose_name=_("Сервис"), on_delete=models.CASCADE,
        related_name='view_logs'
    )
    user = models.ForeignKey(
        User, verbose_name=_("Пользователь"), on_delete=models.SET_NULL,
        null=True, related_name='view_logs',
    )

    class Meta:
        verbose_name = _("Просмотры сервиса")
        verbose_name_plural = _("Просмотры сервиса")
        ordering = ("-created_at",)

    def create_redis_expire(self):
        key = f'{self.service_id}-{self.user_id}'
        expire_in_sec = 60
        red.setex(key, expire_in_sec, 1)

    @staticmethod
    def check_redis_service_view_log(service_id, user_id):
        key = f'{service_id}-{user_id}'
        return red.exists(key)

    def create_redis_expire_v2(self):
        key = f'{self.service_id}-{self.user_id}-{self.category_id}'
        expire_in_sec = 60
        red.setex(key, expire_in_sec, 1)

    @staticmethod
    def check_redis_service_view_log_v2(service_id, user_id, category_id):
        key = f'{service_id}-{user_id}-{category_id}'
        return red.exists(key)


class Transaction(models.Model):
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'

    TYPE_CHOICES = (
        (DEPOSIT, 'Пополнение'),
        (WITHDRAWAL, 'Снятие')
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name='transactions',
        verbose_name="Бизнес"
    )
    amount = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name="Сумма"
    )
    type_of_transaction = models.CharField(
        max_length=10, choices=TYPE_CHOICES, verbose_name="Тип"
    )
    success = models.BooleanField(default=False, verbose_name="Статус")
    description = models.TextField(verbose_name="Описание", default="")

    def __str__(self):
        return (
            f"{self.business.title} - {self.type_of_transaction} - "
            f"{self.amount}"
        )

    class Meta:
        verbose_name = _('Транзакция')
        verbose_name_plural = _('Транзакции')
        ordering = ('-created_at',)

    @staticmethod
    def get_tariff_description(tariff):
        description = (
            f'Оплата за тариф: {tariff.title} - {tariff.price} сом'
        )
        return description


class PayboxPaymentTransaction(models.Model):
    id = models.PositiveIntegerField(
        verbose_name=_("ID Paybox"), unique=True, primary_key=True,
    )

    def __str__(self):
        return str(self.id)


class PayboxOrder(models.Model):
    INIT = 'init'
    FAILED = 'failed'
    SUCCESS = 'success'
    STATUS_CHOICES = (
        (INIT, _(_("Инициализирован"))),
        (FAILED, _("Отклонено")),
        (SUCCESS, _("Успешно")),
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name='paybox_transactions',
        verbose_name=_("Бизнес")
    )
    amount = models.DecimalField(
        verbose_name=_("Сумма"), max_digits=20, decimal_places=2,
        null=True, blank=True
    )
    status = models.CharField(
        verbose_name=_("Статус"), max_length=20, choices=STATUS_CHOICES,
        default=INIT
    )
    description = models.TextField(default="", verbose_name="Описание")
    redirect_url = models.URLField(
        null=True, blank=True, verbose_name=_("Ссылка для оплаты")
    )
    paybox_payment = models.OneToOneField(
        PayboxPaymentTransaction, on_delete=models.PROTECT,
        related_name='paybox_order', null=True, blank=True,
        verbose_name=_("Paybox ID платежа")
    )

    class Meta:
        verbose_name = _("Транзакция Paybox")
        verbose_name_plural = _("Транзакции Paybox")
        ordering = ("-created_at",)

    def set_description(self):
        self.description = f"Пополнение баланса бизнеса: {self.business.title}"
        self.save()

    def get_paybox_init_data(self):
        data = {
            "pg_order_id": self.pk,
            "pg_merchant_id": settings.PAYBOX_MERCHANT_ID,
            "pg_description": self.description,
            "pg_salt": generate_random_string(),
            "pg_currency": settings.PAYBOX_CURRENCY,
            "pg_result_url": settings.PAYBOX_RESULT_URL,
            "pg_request_method": "POST",
            "pg_lifetime": settings.PAYBOX_PAYMENT_LIFETIME_SEC,
            "pg_language": settings.PAYBOX_LANGUAGE,
            "pg_user_id": self.business.user_id,

        }
        if settings.PAYBOX_TEST_MODE:
            data["pg_testing_mode"] = 1

        data["pg_sig"] = self.generate_pg_signature(data)
        return data

    def generate_pg_signature(self, init_data):
        data = copy.deepcopy(init_data)
        sorted_data = sorted(data.items())
        signature_string = ";".join(
            f"{value}" for key, value in sorted_data)
        signature_string = f"any_amount.php;{signature_string};{settings.PAYBOX_SECRET_KEY}"
        return hashlib.md5(signature_string.encode()).hexdigest()

    def get_redirect_url(self):
        data = self.get_paybox_init_data()
        url = "https://api.paybox.money/any_amount.php"
        response = requests.post(url, data=data)
        data = xmltodict.parse(response.text)
        status = data['response']['pg_status']
        is_success = True if status == 'ok' else False
        redirect_url = data['response'].get('pg_redirect_url')
        return redirect_url, is_success
