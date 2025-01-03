from django.contrib import admin
from django.contrib.auth import get_user_model

from notification.models import Notification
from notification.tasks import send_notification_from_admin


User = get_user_model()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'message', 'url', 'for_business']
    fields = ('title', 'message', 'url', 'for_business',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return Notification.objects.filter(for_topic=True)

    def save_model(self, request, obj, form, change):
        users = User.objects.all()
        if not obj.for_business:
            users = users.exclude(business__is_active=True)
        else:
            users = users.filter(business__is_active=True)
        obj.for_topic = True
        obj.save()
        obj.users.add(*users)
        obj.create_redis_view()
        send_notification_from_admin.apply_async(
            kwargs={"notification_id": obj.pk,}
        )
