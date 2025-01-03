from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from django.db.models import Count

from car.models import (
    CarCategory, CarBrand, CarModel, Car, PartCategory, Part,
    PartManufacturerCountry, CarBody, CarDrive
)


@admin.register(CarCategory)
class CarCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'title']


@admin.register(CarBrand)
class CarBrandAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'get_statics')

    def get_statics(self, car_brand):
        request_count, offer_count = (
            CarBrand.objects
            .filter(pk=car_brand.pk)
            .annotate(
                request_count=Count('car_models__purchase_request'),
                offer_count=Count('car_models__purchase_request__offers'))
            .values_list('request_count', 'offer_count')
            .first()
        )
        value = f'Запросы: {request_count}; Ответы: {offer_count}'
        return value

    get_statics.short_description = 'Статистика'


@admin.register(CarModel)
class CarModelAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_filter = ('category', 'brand',)
    search_fields = ('title',)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_filter = ('model',)


@admin.register(PartCategory)
class PartCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Part)
class PartAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('category',)


@admin.register(PartManufacturerCountry)
class PartManufacturerCountry(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(CarBody)
class CarBodyAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(CarDrive)
class CarDriveAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass
