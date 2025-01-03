from celery import shared_task
from django.contrib.auth import get_user_model

from chat.models import ChatRoom
from notification.send_notification import send_message_notification
from src.redis import red
from src.utils import check_and_send_push_notification

User = get_user_model()


@shared_task
def create_new_message_notification(user_id, sender_id, chat_room_id):
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    key = chat_room.get_chat_room_redis_key(sender_id) + '*'
    keys = red.keys(key)
    title = "У вас есть непрочитанные сообщения"
    body = "Проверьте свои чаты. У вас есть непрочитанные сообщения"
    if len(keys) > 0:
        return check_and_send_push_notification(title, user_id, body)
