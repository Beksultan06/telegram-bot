from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from car.models import (
    Car, OilChange, Consumables, CarCategory, CarBrand, CarModel, PartCategory,
    Part, CarBody, PartManufacturerCountry, CarDrive
)
from custom_serializers import CustomDateField, CustomDecimalField


class CarCategorySerializer(ModelSerializer):
    class Meta:
        model = CarCategory
        fields = ('pk', 'title', 'icon')


class CarBrandSerializer(ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ('pk', 'title', 'logo')


class MyCarBrandsSerializer(ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ('pk', 'title')


class CarBrandForBusinessSerializer(ModelSerializer):
    is_added = serializers.SerializerMethodField()

    def get_is_added(self, obj):
        business = self.context['request'].user.business
        return obj.businesses.filter(pk=business.pk).exists()

    class Meta:
        model = CarBrand
        fields = ('pk', 'title', 'is_added')


class CarModelSerializer(ModelSerializer):
    class Meta:
        model = CarModel
        fields = ('pk', 'title')


class CarBodySerializer(ModelSerializer):
    class Meta:
        model = CarBody
        fields = ('pk', 'title')


class CarDriveSerializer(ModelSerializer):
    class Meta:
        model = CarDrive
        fields = ('pk', 'title')


class CarSerializer(ModelSerializer):
    user = serializers.ReadOnlyField(source='user.pk')
    engine_displacement = CustomDecimalField(max_digits=5, decimal_places=1)

    class Meta:
        model = Car
        fields = (
            'pk', 'image', 'year', 'model', 'engine', 'engine_displacement',
            'mileage', 'transmission', 'drive', 'user', 'body'
        )
        extra_kwargs = {
            'body': {'required': True},
            'drive': {'required': True},
        }


class CarDetailSerializer(ModelSerializer):
    user = serializers.ReadOnlyField(source='user.pk')
    engine = serializers.SerializerMethodField()
    transmission = serializers.SerializerMethodField()
    model = CarModelSerializer()
    body = CarBodySerializer()
    drive = CarDriveSerializer()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    def get_engine(self, obj):
        return {
            'title': obj.get_engine_display(),
            'engine': obj.engine,
        }

    def get_transmission(self, obj):
        return {
            'title': obj.get_transmission_display(),
            'transmission': obj.transmission,
        }

    def get_category(self, obj):
        return CarCategorySerializer(
            instance=obj.model.category, context=self.context).data

    def get_brand(self, obj):
        return CarBrandSerializer(
            instance=obj.model.brand, context=self.context).data

    class Meta:
        model = Car
        fields = (
            'pk', 'image', 'year', 'model', 'engine', 'engine_displacement',
            'mileage', 'transmission', 'drive', 'user', 'body', 'category',
            'brand',
        )
        extra_kwargs = {
            'body': {'required': True},
        }


class CarPurchaseRequestSerializer(ModelSerializer):
    title = serializers.CharField(source='get_title_for_purchase_request')

    class Meta:
        model = Car
        fields = ('pk', 'image', 'title',)


class CarListSerializer(ModelSerializer):
    model = serializers.CharField(source='model.__str__')
    body = serializers.CharField(source='body.__str__')
    drive = serializers.CharField(source='drive.__str__')

    class Meta:
        model = Car
        fields = (
            'pk', 'image', 'model', 'year', 'engine_displacement',
            'get_transmission_display', 'drive', 'body',
            'get_engine_display', 'mileage', 'user',
        )


class OilChangeSerializer(ModelSerializer):
    change_date = CustomDateField()

    def create(self, validated_data):
        car_id = validated_data.get('car_id')
        user = self.context['request'].user
        if not user.cars.filter(pk=car_id).exists():
            raise serializers.ValidationError(
                {"message": _("Данный автомобиль не принадлежит пользователю")}
            )
        return super().create(validated_data)

    class Meta:
        model = OilChange
        fields = (
            'pk', 'oil_title', 'current_mileage', 'next_replacement',
            'change_date',
        )


class ConsumablesSerializer(ModelSerializer):
    price = CustomDecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = Consumables
        fields = ('pk', 'title', 'price')


class PartCategorySerializer(ModelSerializer):
    class Meta:
        model = PartCategory
        fields = ('pk', 'title', 'is_common_parts')


class PartSerializer(ModelSerializer):
    class Meta:
        model = Part
        fields = ('pk', 'title', 'category')


class CommonPartForBusinessSerializer(ModelSerializer):
    is_added = serializers.SerializerMethodField()

    def get_is_added(self, part):
        business = self.context['request'].user.business
        return part.businesses.filter(pk=business.pk).exists()

    class Meta:
        model = Part
        fields = ('pk', 'title', 'is_added')


class PartManufacturerCountrySerializer(ModelSerializer):
    class Meta:
        model = PartManufacturerCountry
        fields = ('pk', 'title')
