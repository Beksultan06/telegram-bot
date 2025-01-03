from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from business.serializers import BusinessOfferSerializer
from car.serializers import (
    PartManufacturerCountrySerializer,
    CarModelSerializer, CarBodySerializer, CarDriveSerializer,
    CarCategorySerializer, CarBrandSerializer
)
from custom_serializers import CustomDateTimeField, CustomDecimalField
from purchase_request.models import (
    PurchaseRequest, PurchaseRequestImage, Offer, OfferImage, PurchaseRequestType
)
from purchase_request.tasks import create_new_offer_notification
from user.serializers import UserDetailForPurchaseRequestSerializer
from chat.models import ChatRoom


class CarMixin(serializers.Serializer):
    title = serializers.CharField(source='get_title_for_purchase_request')
    engine = serializers.SerializerMethodField()
    transmission = serializers.SerializerMethodField()
    model = CarModelSerializer()
    body = CarBodySerializer()
    drive = CarDriveSerializer()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    def get_engine(self, obj):
        if hasattr(obj, 'engine'):
            return {
                'title': obj.get_engine_display(),
                'engine': obj.engine,
            }
        return None

    def get_transmission(self, obj):
        if hasattr(obj, 'transmission'):
            return {
                'title': obj.get_transmission_display(),
                'transmission': obj.transmission,
            }
        return None

    def get_category(self, obj):
        if hasattr(obj, "category"):
            return CarCategorySerializer(
                instance=obj.model.category, context=self.context).data
        return None

    def get_brand(self, obj):
        if hasattr(obj, "model"):
            if obj.model:
                return CarBrandSerializer(
                    instance=obj.model.brand, context=self.context).data
        return None

    class Meta:
        fields = [
            'title', 'engine', 'transmission', 'model', 'body', 'drive',
            'category', 'brand', 'car_image', 'year', 'engine_displacement',
            'mileage',
        ]


class OfferImageSerializer(ModelSerializer):
    class Meta:
        model = OfferImage
        fields = ('image', 'pk')


class OfferCreateSerializer(ModelSerializer):
    upload_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False, ),
        write_only=True, required=False
    )
    images = OfferImageSerializer(many=True, read_only=True)
    is_accepted = serializers.SerializerMethodField(read_only=True)
    price = CustomDecimalField(max_digits=10, decimal_places=2, required=True)

    def get_is_accepted(self, offer):
        return offer.chat_room.is_accepted

    def validate(self, attrs):
        attrs = super().validate(attrs)
        purchase_request = attrs.get('purchase_request')
        business = self.context['request'].user.business
        if purchase_request.has_offers_from_this_business(business):
            raise serializers.ValidationError({
                'purchase_request': _('У вас уже есть ответ на данную заявку')
            })
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            images_data = validated_data.pop('upload_images', [])
            offer = Offer.objects.create(**validated_data)
            for image in images_data:
                OfferImage.objects.create(
                    offer=offer, image=image
                )
            offer.create_offer_notification()
            create_new_offer_notification.apply_async(
                kwargs={
                    "user_id": offer.purchase_request.user_id,
                    "request_id": offer.purchase_request_id
                })
            ChatRoom.objects.create(
                offer=offer, purchase_request=offer.purchase_request,
                user=offer.purchase_request.user, business=offer.business
            )
        offer.create_redis_not_viewed_key()
        return offer

    class Meta:
        model = Offer
        fields = (
            'pk', 'created_at', 'part_manufacturer_country', 'difference',
            'condition_of_part', 'price', 'comment', 'chat_room', 'is_accepted',
            'purchase_request', 'availability', 'upload_images', 'images',
        )
        read_only_fields = ('chat_room', 'is_accepted')


class OfferUpdateSerializer(ModelSerializer):
    upload_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    deleted_images = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    images = OfferImageSerializer(many=True, read_only=True)
    price = CustomDecimalField(max_digits=10, decimal_places=2, required=True)

    def update(self, offer, validated_data):
        images_data = validated_data.pop('upload_images', [])
        deleted_images = validated_data.pop('deleted_images', [])
        offer = super().update(offer, validated_data)
        for image in OfferImage.objects.filter(pk__in=deleted_images):
            image.delete()
        for image in images_data:
            OfferImage.objects.create(
                offer=offer, image=image
            )
        return offer

    class Meta:
        model = Offer
        fields = (
            'pk', 'created_at', 'part_manufacturer_country', 'difference',
            'condition_of_part', 'price', 'comment', 'availability',
            'upload_images', 'images', 'deleted_images'
        )


class OfferDetailSerializer(ModelSerializer):
    images = OfferImageSerializer(many=True, read_only=True)
    part_manufacturer_country = PartManufacturerCountrySerializer()
    difference = serializers.SerializerMethodField()
    condition_of_part = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    def get_difference(self, obj):
        return {
            "title": obj.get_difference_display(),
            "value": obj.difference,
        }

    def get_condition_of_part(self, obj):
        return {
            "title": obj.get_condition_of_part_display(),
            "value": obj.condition_of_part,
        }

    def get_availability(self, obj):
        return {
            'title': obj.get_availability_display(),
            'value': obj.availability,
        }

    class Meta:
        model = Offer
        fields = (
            'pk', 'created_at', 'part_manufacturer_country', 'difference',
            'condition_of_part', 'price', 'comment', 'availability',
            'images',
        )


class OfferInfoSerializer(ModelSerializer):
    created_at = CustomDateTimeField()
    images_count = serializers.SerializerMethodField()
    images = OfferImageSerializer(many=True)
    business = BusinessOfferSerializer()
    part_manufacturer_country = serializers.CharField()
    difference = serializers.CharField(source='get_difference_display')
    condition_of_part = serializers.CharField(source='get_condition_of_part_display')
    availability = serializers.CharField(source='get_availability_display')
    part = serializers.SerializerMethodField(method_name='get_part_title')
    car = serializers.CharField(
        source='purchase_request.get_title_for_purchase_request'
    )
    is_accepted = serializers.SerializerMethodField()

    def get_part_title(self, offer):
        if not offer.purchase_request.part:
            return "Нет названия запчасти"
        else:
            return offer.purchase_request.part.title

    def get_images_count(self, value):
        return value.images.count()

    def get_is_accepted(self, offer):
        return offer.chat_room.is_accepted

    class Meta:
        model = Offer
        fields = (
            'pk', 'created_at', 'part_manufacturer_country', 'difference',
            'condition_of_part', 'availability', 'price', 'chat_room', 'is_accepted',
            'images_count', 'comment', 'business', 'images', 'part', 'car',
        )


class OfferNotificationSerializer(ModelSerializer):
    part = serializers.SerializerMethodField(method_name='get_part_title')
    car = serializers.CharField(
        source='purchase_request.get_title_for_purchase_request'
    )
    image = serializers.ImageField(source='purchase_request.car_image')

    class Meta:
        model = Offer
        fields = (
            'pk', 'part', 'car', 'image'
        )

    def get_part_title(self, offer):
        if not offer.purchase_request.part:
            return "Нет названия запчасти"
        else:
            return offer.purchase_request.part.title


class PurchaseRequestImageSerializer(ModelSerializer):
    class Meta:
        model = PurchaseRequestImage
        fields = ('pk', 'image',)


class PurchaseRequestTypeSerializer(ModelSerializer):
    class Meta:
        model = PurchaseRequestType
        fields = '__all__'


class PurchaseRequestCreateSerializer(ModelSerializer):
    upload_images = serializers.ListField(
        child=serializers.ImageField(
            allow_empty_file=False, use_url=False,
        ), write_only=True, required=False
    )
    images = PurchaseRequestImageSerializer(many=True, read_only=True)
    created_at = CustomDateTimeField(read_only=True)

    def create(self, validated_data):
        with transaction.atomic():
            images_data = validated_data.pop('upload_images', [])
            purchase_request = PurchaseRequest.objects.create(**validated_data)

            for image in images_data:
                PurchaseRequestImage.objects.create(
                    purchase_request=purchase_request, image=image
                )

        return purchase_request

    class Meta:
        model = PurchaseRequest
        fields = (
            'pk', 'created_at', 'description', 'region',
            'part', 'images', 'upload_images', 'type',

            # car fields
            'car_image', 'year', 'model', 'engine', 'engine_displacement',
            'mileage', 'vin_code', 'transmission', 'drive', 'body'
        )
        extra_kwargs = {
            'model': {'required': True},
            'year': {'required': True},
            'part': {'required': True},
        }


class VipPurchaseRequestCreateSerializer(ModelSerializer):
    created_at = CustomDateTimeField(read_only=True)

    def create(self, validated_data):
        with transaction.atomic():
            purchase_request = PurchaseRequest.objects.create(**validated_data)
        return purchase_request

    class Meta:
        model = PurchaseRequest
        fields = (
            'pk', 'created_at', 'description', 'type',
        )

class PurchaseRequestUpdateSerializer(ModelSerializer):
    upload_images = serializers.ListField(
        child=serializers.ImageField(
            allow_empty_file=False, use_url=False,
        ), write_only=True, required=False
    )
    deleted_images = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    images = PurchaseRequestImageSerializer(many=True, read_only=True)

    def update(self, instance, validated_data):
        images_data = validated_data.pop('upload_images', [])
        deleted_images = validated_data.pop('deleted_images', [])
        instance = super().update(instance, validated_data)

        for image in PurchaseRequestImage.objects.filter(pk__in=deleted_images):
            image.delete()

        for image in images_data:
            PurchaseRequestImage.objects.create(
                purchase_request=instance, image=image
            )
        return instance

    class Meta:
        model = PurchaseRequest
        fields = (
            'pk', 'description', 'region', 'part', 'images',
            'upload_images', 'deleted_images',

            # car fields
            'car_image', 'year', 'model', 'engine', 'engine_displacement',
            'mileage', 'vin_code', 'transmission', 'drive', 'body'
        )
        extra_kwargs = {
            'model': {'required': True},
            'year': {'required': True},
        }


class PurchaseRequestUpdateDetailSerializer(CarMixin, ModelSerializer):
    images = PurchaseRequestImageSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = [
                     'pk', 'description', 'region', 'part', 'images'
                 ] + CarMixin.Meta.fields


class PurchaseRequestListSerializer(CarMixin, ModelSerializer):
    part = serializers.CharField(source='part.title', read_only=True)
    new_offers_count = serializers.IntegerField(source='get_new_offers_count')
    created_at = CustomDateTimeField()

    class Meta:
        model = PurchaseRequest
        fields = [
                     'pk', 'created_at', 'part', 'new_offers_count', 'is_paid', 'description',
                 ] + CarMixin.Meta.fields


class PurchaseRequestDetailSerializer(CarMixin, ModelSerializer):
    part = serializers.CharField(source='part.title', read_only=True)
    images = PurchaseRequestImageSerializer(many=True, required=False)
    created_at = CustomDateTimeField()
    offers = serializers.SerializerMethodField()

    def get_offers(self, obj):
        offers = obj.offers.all().order_by(
            'business__tariff__my_order', '-created_at'
        )
        return OfferInfoSerializer(offers, many=True, context=self.context).data

    class Meta:
        model = PurchaseRequest
        fields = [
                     'pk', 'created_at', 'part', 'description', 'images',
                     'is_active', 'offers',
                 ] + CarMixin.Meta.fields


class PurchaseRequestOffSerializer(ModelSerializer):

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return instance

    class Meta:
        model = PurchaseRequest
        fields = ('pk', 'is_active')
        read_only_fields = ('pk', 'is_active')


class PurchaseRequestForBusinessListSerializer(CarMixin, ModelSerializer):
    part = serializers.CharField(source='part.title', read_only=True)
    user = UserDetailForPurchaseRequestSerializer(read_only=True)
    created_at = CustomDateTimeField()
    region = serializers.SerializerMethodField()
    offer = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    images = PurchaseRequestImageSerializer(many=True, required=False)

    def get_region(self, instance):
        if instance.region:
            return instance.region.title
        return "Нет региона"

    def get_offer(self, purchase_request):
        business = self.context['request'].user.business
        offer = purchase_request.offers.filter(business=business).first()
        if not offer:
            return {}
        return OfferInfoSerializer(instance=offer, context=self.context).data

    def get_is_viewed(self, instance):
        user = self.context['request'].user
        return instance.get_is_viewed_by_request_user(user)

    def get_views(self, instance):
        return instance.viewed_users_count()

    class Meta:
        model = PurchaseRequest
        fields = [
                     'pk', 'created_at', 'part', 'user', 'region',
                     'description', 'images', 'offer', 'is_viewed', 'views', 'vin_code'
                 ] + CarMixin.Meta.fields


class AcceptedOfferListSerializer(OfferInfoSerializer):
    car = serializers.CharField(source='purchase_request.model')
    part = serializers.SerializerMethodField(method_name='get_part_title')
    new_messages_count = serializers.IntegerField(
        source='chat_room.get_new_messages_count_user'
    )

    def get_part_title(self, offer):
        if not offer.purchase_request.part:
            return "Нет названия запчасти"
        else:
            return offer.purchase_request.part.title

    class Meta:
        model = Offer
        fields = (
            'pk', 'created_at', 'part_manufacturer_country', 'difference',
            'condition_of_part', 'availability', 'price', 'chat_room', 'part',
            'car', 'comment', 'new_messages_count', 'business', 'images',
        )


class AcceptedPurchaseRequestForBusinessListSerializer(PurchaseRequestForBusinessListSerializer):
    chat_room = serializers.SerializerMethodField()

    def get_chat_room(self, purchase_request):
        business = self.context['request'].user.business
        offer = purchase_request.offers.filter(business=business).first()
        if not offer:
            return {}
        data = {
            "chat_room": offer.chat_room.pk,
            "new_messages_count": offer.chat_room.get_new_messages_count_business()
        }
        return data

    class Meta:
        model = PurchaseRequest
        fields = [
                     'pk', 'created_at', 'part', 'user', 'region', 'offer',
                     'chat_room',
                 ] + CarMixin.Meta.fields
