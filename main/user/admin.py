from django.contrib import admin
from rest_framework.authtoken.models import Token, TokenProxy
from rest_framework.authtoken.admin import TokenAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'name', 'created_at', 'profile_photo', 'verification_code', 'is_active']
    readonly_fields = (
        'phone_number', 'name', 'created_at', 'profile_photo',
        'verification_code',
    )
    search_fields = ('phone_number', 'name')
    list_filter = ['is_active']

    def has_add_permission(self, request):
        return False


admin.site.unregister(TokenProxy)

@admin.register(TokenProxy)
class MyTokenAdmin(TokenAdmin):
    search_fields = ['user__phone_number']
