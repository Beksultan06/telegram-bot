from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from business.mixins import BusinessPhoneNumbersValidateMixin
from business.models import (
    Business, ServiceCategory, Service, Tariff,
    ServiceSubCategory, Transaction, ServiceViewLog, PayboxOrder
)
from car.models import PartCategory
from custom_serializers import CustomTimeField, CustomDecimalField
from info.serializers import RegionSerializer


class TariffSerializer(ModelSerializer):
    is_actual = serializers.SerializerMethodField()

    def get_is_actual(self, obj):
        if obj.pk == self.context['request'].user.business.tariff_id:
            return True
        return False

    class Meta:
        model = Tariff
        fields = (
            'pk', 'title', 'logo', 'price', 'old_price', 'is_actual', 'description',
            'car_brands_count', 'common_parts_count',
        )


class TariffChangeSerializer(ModelSerializer):
    class Meta:
        model = Business
        fields = ('tariff',)

    def validate_tariff(self, tariff):
        if self.instance.tariff == tariff:
            raise serializers.ValidationError(_("Вы уже на данном тарифе"))
        return tariff

    def update(self, business, validated_data):
        tariff = validated_data['tariff']
        transaction = Transaction(
            business=business, amount=tariff.price,
            type_of_transaction=Transaction.WITHDRAWAL,
            description=Transaction.get_tariff_description(tariff)
        )

        try:
            business = Business.decrease_balance(business.pk, tariff.price)
        except ValueError as error:
            transaction.success = False
            transaction.save()
            raise serializers.ValidationError({
                "message": str(error)
            })
        business = super().update(business, validated_data)
        business.set_tariff_end_day()
        business.update_car_brands_and_common_parts_by_tariff()
        transaction.success = True
        transaction.save()
        return business

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({"message": _("Тариф успешно обновлен")})
        return data


class BusinessSerializer(BusinessPhoneNumbersValidateMixin, ModelSerializer):
    tariff = serializers.SlugRelatedField(slug_field='pk', read_only=True)

    def create(self, validated_data):
        user = validated_data['user']
        if user.is_business:
            raise serializers.ValidationError(({
                'user': [_('Данный пользователь уже является бизнес аккаунтом')]
            }))
        elif hasattr(user, 'business'):
            user.business.activate()
            return user.business
        business = super().create(validated_data)
        business.balance = settings.BUSINESS_START_BALANCE
        business.set_standard_tariff()
        return business

    class Meta:
        model = Business
        fields = (
            'pk', 'title', 'address', 'telegram', 'instagram',
            'tiktok', 'whatsapp', 'image', 'first_phone_number',
            'second_phone_number', 'third_phone_number', 'tariff',
            'types_of_purchase_requests', 'balance'
        )
        read_only_fields = ('balance',)


class Api2BusinessSerializer(BusinessPhoneNumbersValidateMixin, ModelSerializer):
    tariff = serializers.SlugRelatedField(slug_field='pk', read_only=True)

    def create(self, validated_data):
        user = validated_data['user']
        if user.is_business:
            raise serializers.ValidationError(({
                'user': [_('Данный пользователь уже является бизнес аккаунтом')]
            }))
        elif hasattr(user, 'business'):
            user.business.activate()
            return user.business
        business = super().create(validated_data)
        business.balance = settings.BUSINESS_START_BALANCE
        business.save()
        return business

    class Meta:
        model = Business
        fields = (
            'pk', 'title', 'address', 'telegram', 'instagram',
            'tiktok', 'whatsapp', 'image', 'first_phone_number',
            'second_phone_number', 'third_phone_number', 'tariff',
            'types_of_purchase_requests', 'balance', 'is_tariff_selected', 'is_car_brands_selected',
        )
        read_only_fields = ('balance',)


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            'pk', 'title', 'address', 'telegram', 'instagram',
            'tiktok', 'whatsapp', 'image', 'first_phone_number',
            'second_phone_number', 'third_phone_number', 'tariff',
            'types_of_purchase_requests', 'balance'
        )


class BusinessActivateSerializer(ModelSerializer):

    def update(self, instance, validated_data):
        self.instance.activate()
        return self.instance

    class Meta:
        model = Business
        fields = ('pk', 'is_active')
        extra_kwargs = {
            'is_active': {'read_only': True},
        }


class BusinessDeactivateSerializer(ModelSerializer):

    def update(self, instance, validated_data):
        self.instance.deactivate()
        return self.instance

    class Meta:
        model = Business
        fields = ('pk', 'is_active')
        extra_kwargs = {
            'is_active': {'read_only': True},
        }


class ServiceCategorySerializer(ModelSerializer):
    service_count = serializers.IntegerField(source='services.count')
    sub_categories_count = serializers.IntegerField(
        source='sub_categories.count'
    )

    class Meta:
        model = ServiceCategory
        fields = (
            'pk', 'title', 'image', 'has_sub_categories', 'service_count',
            'sub_categories_count'
        )


class ServiceSubCategorySerializer(ModelSerializer):
    class Meta:
        model = ServiceSubCategory
        fields = ('pk', 'title')


class ServiceSerializer(BusinessPhoneNumbersValidateMixin, ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all(), many=True)
    work_days = serializers.MultipleChoiceField(choices=Service.DAY_CHOICES)
    start_time = CustomTimeField()
    end_time = CustomTimeField()

    class Meta:
        model = Service
        fields = (
            'pk', 'title', 'address', 'comment', 'work_days', 'image',
            'start_time', 'end_time', 'category', 'categories', 'sub_category',
            'telegram', 'instagram', 'tiktok', 'whatsapp',
            'first_phone_number', 'second_phone_number', 'third_phone_number',
            'region'
        )
        extra_kwargs = {
            'category': {'required': True},
        }


class ServiceDetailSerializer(BusinessPhoneNumbersValidateMixin, ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all(), many=True)
    work_days = serializers.MultipleChoiceField(choices=Service.DAY_CHOICES)
    start_time = CustomTimeField()
    end_time = CustomTimeField()
    category = ServiceCategorySerializer()
    sub_category = ServiceSubCategorySerializer()
    region = RegionSerializer(many=True)

    class Meta:
        model = Service
        fields = (
            'pk', 'title', 'address', 'comment', 'work_days', 'image',
            'start_time', 'end_time', 'category', 'categories', 'sub_category',
            'telegram', 'instagram', 'tiktok', 'whatsapp',
            'first_phone_number', 'second_phone_number', 'third_phone_number',
            'region'
        )
        extra_kwargs = {
            'category': {'required': True},
        }


class BusinessCarBrandSerializer(ModelSerializer):
    class Meta:
        model = Business
        fields = ('pk', 'car_brands')

    def update(self, instance, validated_data):
        car_brands = validated_data.get('car_brands')
        if car_brands:
            instance.car_brands.clear()
            instance.car_brands.add(*car_brands)
        else:
            instance.car_brands.clear()
        return instance

    def validate(self, attrs):
        car_brands = attrs.get('car_brands')
        if car_brands and len(car_brands) > self.instance.tariff.car_brands_count:
            raise serializers.ValidationError(
                {"car_models": _(
                    "Вы не можете добавить новую марку машины. "
                    "К сожалению вы превысили кол-во машин, доступных "
                    "у вас в тарифе"
                )}
            )
        return attrs


class BusinessCommonParsSerializer(ModelSerializer):

    def validate(self, attrs):
        common_parts = attrs.get('common_parts')
        if common_parts and len(common_parts) > self.instance.tariff.common_parts_count:
            raise serializers.ValidationError(
                {"common_parts_business": _(
                    f"Вы не можете добавить столько общих деталей "
                    f"({len(common_parts)}. "
                    "К сожалению вы превысили кол-во общих деталей, доступных "
                    f"у вас в тарифе ({self.instance.tariff.common_parts_count})"
                )}
            )
        category = PartCategory.objects.filter(is_common_parts=True).first()
        if not category:
            raise serializers.ValidationError(
                {"common_parts_business": _(
                    _("Пока еще нету категории для общих деталей")
                )}
            )
        for part in common_parts:
            if part.category != category:
                raise serializers.ValidationError(
                    {"common_parts_business": _(
                        _("Некоторые детали не являются общими")
                    )}
                )
        return attrs

    class Meta:
        model = Business
        fields = ('pk', 'common_parts')


class BusinessOfferSerializer(ModelSerializer):
    class Meta:
        model = Business
        fields = (
            'pk', 'title', 'image', 'telegram', 'instagram',
            'tiktok', 'whatsapp', 'address', 'first_phone_number',
            'second_phone_number', 'third_phone_number',
        )


class ServiceViewLogCreateSerializer(ModelSerializer):

    def validate_service(self, service):
        user = self.context['request'].user
        redis_log = ServiceViewLog.check_redis_service_view_log(
            service_id=service.pk, user_id=user.pk
        )
        if redis_log:
            raise serializers.ValidationError(
                _("Просмотрено менее 1 мин назад")
            )
        return service

    def create(self, validated_data):
        log = super().create(validated_data)
        log.create_redis_expire()
        return log

    class Meta:
        model = ServiceViewLog
        fields = ('pk', 'service')


class Api2ServiceViewLogCreateSerializer(ModelSerializer):

    def validate_service(self, service):
        user = self.context['request'].user
        category = self.context['request'].query_params.get('category')
        redis_log = ServiceViewLog.check_redis_service_view_log_v2(
            service_id=service.pk, user_id=user.pk, category_id=category
        )
        if redis_log:
            raise serializers.ValidationError(
                _("Просмотрено менее 1 мин назад")
            )
        return service

    def create(self, validated_data):
        log = super().create(validated_data)
        log.create_redis_expire_v2()
        return log

    class Meta:
        model = ServiceViewLog
        fields = ('pk', 'service', 'category')


class PayboxOrderSerializer(ModelSerializer):

    def create(self, validated_data):
        with transaction.atomic():
            obj = super().create(validated_data)
            obj.set_description()
            obj.redirect_url, is_success = obj.get_redirect_url()
            if not is_success:
                raise serializers.ValidationError(
                    {"redirect_url": _("Сервис временно недоступен")}
                )
            obj.save()
        return obj

    class Meta:
        model = PayboxOrder
        fields = ("id", "redirect_url")
        read_only_fields = ("id", "redirect_url")


class StaticsCarBrandSerializer(serializers.Serializer):
    title = serializers.CharField()
    logo = serializers.ImageField()
    request_count = serializers.IntegerField(default=0)
    offer_count = serializers.IntegerField(default=0)


class StaticsServiceSerializer(ModelSerializer):
    view_count = serializers.IntegerField(default=0)
    category_title = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ('pk', 'title', 'image', 'address', 'view_count', 'category_title')

    def get_category_title(self, instance):
        return instance.category.title


class ServiceViewLogSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    service_title = serializers.CharField()
    view_count = serializers.IntegerField()
    address = serializers.CharField()
    image = serializers.ImageField()


class CategoryServiceViewLogSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    services = ServiceViewLogSerializer(many=True)
