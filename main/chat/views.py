from django.db.models import Q

from rest_framework.generics import ListCreateAPIView
from django.http import Http404

from chat.models import Message, ChatRoom
from chat.paginators import ChatPagination
from chat.serializers import MessageSerializer
from purchase_request.serializers import OfferInfoSerializer


class MessageCreateListView(ListCreateAPIView):
    serializer_class = MessageSerializer
    pagination_class = ChatPagination

    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        chat_room = ChatRoom.objects.filter(pk=kwargs.get('chat_room')).first()
        if chat_room:
            chat_room.clear_new_messages_count(user=self.request.user)
        else:
            raise Http404
        response.data['offer'] = OfferInfoSerializer(
            instance=chat_room.offer, context=self.get_serializer_context()
        ).data
        return response

    def get_queryset(self, *args, **kwargs):
        chat_room_id = self.kwargs.get('chat_room')
        queryset = (
            Message.objects
            .filter(chat_room_id=chat_room_id)
            .filter(
                Q(chat_room__user=self.request.user) |
                Q(chat_room__business__user=self.request.user)
            )
        ).select_related('chat_room__offer')
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            chat_room_id=self.kwargs['chat_room'], sender=self.request.user
        )
