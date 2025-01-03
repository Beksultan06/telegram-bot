from datetime import timedelta

from rest_framework import serializers
from django.utils import timezone

from src.redis import red
from custom_serializers import CustomDateTimeField
from chat.models import Message
from chat.tasks import create_new_message_notification


class MessageSerializer(serializers.ModelSerializer):
    created_at = CustomDateTimeField(read_only=True)

    def create(self, validated_data):
        message = super().create(validated_data)
        chat_room = message.chat_room
        if message.sender == chat_room.user and not chat_room.is_accepted:
            chat_room.is_accepted = True
            chat_room.save()
            chat_room.offer.accept_offer_notification()
        message.create_redis_view_status()

        key = f'chat_room:{message.chat_room_id};task_status'
        if red.exists(key):
            return message
        red.setex(key, 10, 'true')
        user_id = message.chat_room.user_id
        if user_id == message.sender_id:
            user_id = message.chat_room.business.user_id

        eta_time = timezone.now() + timedelta(seconds=9)
        create_new_message_notification.apply_async(
            eta=eta_time, kwargs={
                "user_id": user_id,
                "sender_id": message.sender_id,
                "chat_room_id": message.chat_room_id
            }
        )
        return message

    class Meta:
        model = Message
        fields = ('pk', 'sender', 'message', 'created_at', 'chat_room')
        read_only_fields = ('pk', 'sender', 'chat_room', 'created_at')
