from django.contrib import admin
from django.contrib.admin import TabularInline

from product.forms import ProductAdminForm
from product.models import Product, ProductImage


# Register your models here.
class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):

    form = ProductAdminForm
    list_display = ('title', 'car_model', 'car_brand', 'year', 'price')

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
                'car_model',
                'car_brand',
                'car_category',
                'part',
                'manufacturer_country',
                ('price', 'shop_price'),  # Эти два поля будут на одной строке
                'year',
                'shop',
                'availability',
                'condition_of_part',
                'difference',
            )
        }),
    )
    inlines = [ProductImageInline]


admin.site.register(Product, ProductAdmin)
