from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from business.models import Business
from purchase_request.models import PurchaseRequest, Offer
from src.redis import red

User = get_user_model()


class ChatRoom(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, verbose_name=_('Пользователь'), on_delete=models.CASCADE,
        related_name='chat_rooms',
    )
    business = models.ForeignKey(
        Business, verbose_name=_('Бизнес'), on_delete=models.CASCADE,
        related_name='chat_rooms', db_index=True
    )
    purchase_request = models.ForeignKey(
        PurchaseRequest, verbose_name=_('Заявка'), on_delete=models.CASCADE,
        related_name='chat_rooms',
    )
    offer = models.OneToOneField(
        Offer, verbose_name=_('Ответ на заявку'), on_delete=models.CASCADE,
        related_name='chat_room'
    )
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.business}: {self.purchase_request.pk}'

    def get_chat_room_redis_key(self, user_id):
        key = f'chat_room:{self.pk};user:{user_id};message:'
        return key

    def get_new_messages_count_user(self):
        key = self.get_chat_room_redis_key(user_id=self.business.user_id) + '*'
        keys = red.keys(key)
        return len(keys)

    def get_new_messages_count_business(self):
        key = self.get_chat_room_redis_key(user_id=self.user_id) + '*'
        keys = red.keys(key)
        return len(keys)

    def clear_new_messages_count(self, user):
        if self.user_id == user.pk:
            user_id = self.business.user_id
        else:
            user_id = self.user_id

        key = self.get_chat_room_redis_key(user_id=user_id) + '*'
        keys = red.keys(key)
        if keys:
            red.delete(*keys)


class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    chat_room = models.ForeignKey(
        ChatRoom, verbose_name=_('Чат'), related_name='messages',
        on_delete=models.CASCADE, db_index=True
    )
    sender = models.ForeignKey(
        User, verbose_name=_('Отправитель'), related_name='messages',
        on_delete=models.CASCADE
    )
    message = models.TextField()

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('-created_at',)

    def create_redis_view_status(self):
        chat_room_key = self.chat_room.get_chat_room_redis_key(
            user_id=self.sender_id
        )
        key = f'{chat_room_key}{self.pk}'
        red.set(key, 1)
