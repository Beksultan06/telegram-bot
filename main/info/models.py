from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel

from src.redis import red
from utils import custom_upload_path


class Region(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    sub_title = models.CharField(
        _("Подзаголовок"), max_length=100, null=True, blank=True
    )
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        if self.sub_title:
            return f'{self.title} {self.sub_title}'
        return self.title

    class Meta:
        verbose_name = _("Регион")
        verbose_name_plural = _("Регионы")
        ordering = ['my_order']


class PromotionalCodesAndDiscount(models.Model):
    title = models.CharField(_("Название"), max_length=100)
    sub_title = models.CharField(
        _("Подзаголовок"), max_length=100, null=True, blank=True
    )
    description = models.TextField(_("Описание"))
    image = models.ImageField(_('Изображение'), upload_to=custom_upload_path)
    url = models.URLField(_('Ссылка'))
    region = models.ManyToManyField(Region, related_name='promotional_codes')
    is_active = models.BooleanField(_('Активный'), default=True)
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )
    count = models.PositiveIntegerField(default=0, verbose_name='Количество переходов', editable=False)

    def increment_click_count(self, user_id):
        """
        Увеличивает счетчик кликов, если пользователь не заходил на страницу в течение последней минуты.
        :param user_id: Идентификатор пользователя
        """
        banner_id = self.id
        redis_key = f'banner:{banner_id}:user:{user_id}'
        # Проверяем, был ли пользователь уже на этой странице в течение последней минуты
        if not red.exists(redis_key):
            self.count += 1
            self.save()
            # Устанавливаем ключ в Redis с истечением срока действия в 60 секунд
            red.setex(redis_key, timedelta(minutes=1), 1)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Промокоды и скидки")
        verbose_name_plural = _("Промокоды и скидки")
        ordering = ['my_order']


class Banner(models.Model):
    class Meta:
        verbose_name = _("Баннер")
        verbose_name_plural = _("Баннеры")

    title = models.CharField(_("Название"), max_length=100)
    sub_title = models.CharField(
        _("Подзаголовок"), max_length=100, null=True
    )
    description = models.TextField(_("Описание"))
    image = models.ImageField(_('Изображение'), upload_to=custom_upload_path)
    url = models.URLField(_('Ссылка'))
    is_active = models.BooleanField(_('Активный'), default=True)
    count = models.PositiveIntegerField(default=0, verbose_name='Количество посещений', editable=False)

    def __str__(self):
        return self.title

    def increment_click_count(self, user_id):
        """
        Увеличивает счетчик кликов, если пользователь не заходил на страницу в течение последней минуты.
        :param user_id: Идентификатор пользователя
        """
        banner_id = self.id
        redis_key = f'banner:{banner_id}:user:{user_id}'
        # Проверяем, был ли пользователь уже на этой странице в течение последней минуты
        if not red.exists(redis_key):
            self.count += 1
            self.save()
            # Устанавливаем ключ в Redis с истечением срока действия в 60 секунд
            red.setex(redis_key, timedelta(minutes=1), 1)


class AboutApp(SingletonModel):
    description = models.TextField(_("Описание"))
    privacy_policy = models.URLField(
        _("Политика конфиденциальности"), blank=True, null=True
    )
    data_processing_policy = models.URLField(
        _("Политика обработки данных"), blank=True, null=True
    )

    def __str__(self):
        return 'О приложении'

    class Meta:
        verbose_name = _('О приложении')
        verbose_name_plural = _('О приложении')


class VersionControl(SingletonModel):
    android_version = models.CharField(
        max_length=255, verbose_name="Версия приложения"
    )
    android_force_update = models.BooleanField(
        default=False, verbose_name="Принудительное обновление"
    )
    ios_version = models.CharField(
        max_length=255, verbose_name="Версия приложения"
    )
    ios_force_update = models.BooleanField(
        default=False, verbose_name="Принудительное обновление"
    )

    class Meta:
        verbose_name = "Управление версией приложения"

    def __str__(self):
        return f'Android: {self.android_version}    IOS: {self.ios_version}'


class FAQ(models.Model):
    question = models.TextField(_('Вопрос'))
    answer = models.TextField(_('Ответ'))
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = _('Вопросы и ответы')
        verbose_name_plural = _('Вопросы и ответы')
        ordering = ['my_order']


class Ad(SingletonModel):
    title = models.CharField(_('Заголовок'), max_length=100)
    sub_title = models.CharField(
        _('Подзаголовок'), max_length=100, blank=True, null=True
    )
    description = models.TextField(_('Описание'))
    image = models.ImageField(_('Изображение'), upload_to=custom_upload_path)
    my_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, verbose_name=_('Очередь')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Реклама')
        verbose_name_plural = _('Рекламы')
        ordering = ['my_order']


class Support(SingletonModel):
    phone_number = models.CharField(
        _("Номер телефона для поддержки"), max_length=20
    )
    ad_phone_number = models.CharField(
        _("Номер телефона для рекламы"), max_length=20
    )

    def __str__(self):
        return 'Поддержка'

    class Meta:
        verbose_name = _('Поддержка')
        verbose_name_plural = _('Поддержка')
