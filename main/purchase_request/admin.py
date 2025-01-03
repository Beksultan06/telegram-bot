from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from purchase_request.models import PurchaseRequest, Offer, PurchaseRequestType


# Register your models here.

class OfferInline(admin.TabularInline):
    model = Offer

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PurchaseRequestType)
class PurchaseRequestTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "text", "my_order",)


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'model', 'year', 'part', 'region', 'created_at', 'updated_at', 'user', 'description',
                    'is_active', 'get_all_offers', 'get_viewed_users_count']
    inlines = [
        OfferInline,
    ]

    def get_viewed_users_count(self, obj):
        return obj.viewed_users_count()

    get_viewed_users_count.short_description = 'Количество просмотров'

    def get_all_offers(self, obj):
        return obj.offers.count()

    get_all_offers.short_description = 'Количество ответов'

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'purchase_request', 'created_at', 'price', 'availability', 'updated_at', 'business',
                    'comment']
    search_fields = ['purchase_request__id', ]

    def has_change_permission(self, request, obj=None):
        return False
