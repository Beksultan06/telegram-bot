from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin
from django.utils.html import format_html

from business.models import (
    Tariff, ServiceCategory, ServiceSubCategory, Service, Business,
    Transaction, PayboxOrder
)


@admin.register(Tariff)
class TariffAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'price', 'car_brands_count', 'common_parts_count')


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'business_user_name', 'tariff', 'tariff_end_day', 'balance', 'first_phone_number',
                    'created_at', 'is_active']

    search_fields = ('title',)
    list_filter = ['tariff', 'is_active']

    def save_model(self, request, obj, form, change):
        old_balance = form.initial.get('balance', 0)
        super().save_model(request, obj, form, change)
        changed_fields = form.changed_data
        if 'balance' in changed_fields:
            obj.refresh_from_db()
            new_balance = obj.balance
            if new_balance > old_balance:
                type_of_transaction = Transaction.DEPOSIT
                amount = new_balance - old_balance
            elif new_balance < old_balance:
                type_of_transaction = Transaction.WITHDRAWAL
                amount = old_balance - new_balance
            else:
                return
            Transaction.objects.create(
                business=obj, amount=amount, success=True,
                type_of_transaction=type_of_transaction,
                description=f"Ручное обновление баланса через админ панель."
                            f"\nПрошлый баланс - {old_balance}"
                            f"\nСейчас - {new_balance}"
            )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title',)


# @admin.register(ServiceSubCategory)
# class ServiceSubCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
#     search_fields = ('title',)
#     list_display = ('title', 'category')
#     list_filter = ('category',)


@admin.register(Service)
class ServiceAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_filter = ('category', 'categories', 'region')
    list_display = ('title', 'category', 'sub_category', 'get_views', 'image_tag')
    search_fields = ('title', 'category__title', 'sub_category__title')
    readonly_fields = ('created_at', 'updated_at')

    def get_views(self, service):
        return service.view_logs.count()

    get_views.short_description = 'Просмотры'

    def image_tag(self, obj):
        return format_html('<img src="{}" width="auto" height="30px" />'.format(obj.get_image()))

    image_tag.short_description = 'Фото'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'amount', 'type_of_transaction', 'success',
        'description',
    )
    readonly_fields = (
        'created_at', 'business', 'amount', 'type_of_transaction',
        'success', 'description',
    )
    search_fields = ('created_at',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PayboxOrder)
class PayboxOrderAdmin(admin.ModelAdmin):
    list_display = ('business', 'created_at', 'amount', 'status')
    readonly_fields = (
        'business', 'created_at', 'amount', 'status', 'description',
        'paybox_payment'
    )
    exclude = ('redirect_url',)
