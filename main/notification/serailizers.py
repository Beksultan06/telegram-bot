from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from custom_serializers import CustomDateTimeField
from notification.models import Notification
from purchase_request.serializers import OfferNotificationSerializer


class NotificationPushSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = ('message',)


class NotificationSerializer(ModelSerializer):
    created_at = CustomDateTimeField()
    offer = OfferNotificationSerializer(read_only=True)
    is_new_notification = serializers.SerializerMethodField()

    def get_is_new_notification(self, instance):
        user = self.context['request'].user
        return instance.get_user_viewed_status(user=user)

    class Meta:
        model = Notification
        fields = (
            'pk', 'created_at', 'title', 'message', 'tariff',
            'offer', 'is_new_notification', 'url'
        )
