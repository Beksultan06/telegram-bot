from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from info.models import (
    Region, PromotionalCodesAndDiscount, Banner, AboutApp, FAQ, Support, Ad, VersionControl)


@admin.register(Region)
class RegionAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(PromotionalCodesAndDiscount)
class PromotionalCodesAndDiscountAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'count']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active', 'count']


@admin.register(AboutApp)
class AboutAppAdmin(SingletonModelAdmin):
    pass


@admin.register(FAQ)
class FAQAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Support)
class SupportAdmin(SingletonModelAdmin):
    pass


@admin.register(Ad)
class AdAdmin(SortableAdminMixin, SingletonModelAdmin):
    pass


@admin.register(VersionControl)
class VersionControlAdmin(SingletonModelAdmin):
    fieldsets = (
        ('Android', {'fields': ('android_version', 'android_force_update')}),
        ('IOS', {'fields': ('ios_version', 'ios_force_update')}),
    )
