from datetime import timedelta

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView,
    RetrieveUpdateAPIView, DestroyAPIView
)
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatRoom
from purchase_request.models import PurchaseRequest, Offer, PurchaseRequestType
from purchase_request.serializers import (
    PurchaseRequestListSerializer, PurchaseRequestCreateSerializer,
    PurchaseRequestDetailSerializer, PurchaseRequestOffSerializer,
    PurchaseRequestUpdateSerializer, AcceptedOfferListSerializer,
    PurchaseRequestUpdateDetailSerializer, PurchaseRequestTypeSerializer, VipPurchaseRequestCreateSerializer,
)


class PurchaseRequestTypeListView(ListAPIView):
    serializer_class = PurchaseRequestTypeSerializer
    queryset = PurchaseRequestType.objects.all()


class PurchaseRequestCreateView(CreateAPIView):
    serializer_class = PurchaseRequestCreateSerializer
    queryset = PurchaseRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VipPurchaseRequestCreateView(CreateAPIView):
    serializer_class = VipPurchaseRequestCreateSerializer
    queryset = PurchaseRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PurchaseRequestUpdateView(RetrieveUpdateAPIView):
    serializer_class = PurchaseRequestUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PurchaseRequestUpdateDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        return PurchaseRequest.objects.filter(user=self.request.user)


class PurchaseRequestListView(ListAPIView):
    serializer_class = PurchaseRequestListSerializer

    def get_queryset(self):
        # now = timezone.now()
        # last_24_hour = timezone.now() - timedelta(hours=24)
        queryset = (
            PurchaseRequest.objects.
            filter(is_active=True, user=self.request.user).
            select_related('model', 'part')
        )

        return queryset.distinct()


class PurchaseRequestDetailView(RetrieveAPIView):
    serializer_class = PurchaseRequestDetailSerializer

    def get_queryset(self):
        queryset = (
            PurchaseRequest.objects.
            filter(user=self.request.user).
            select_related('model', 'part').
            prefetch_related(
                'offers', 'offers__business', 'offers__business__tariff'
            )
        )
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        instance.view_new_offers()
        return Response(serializer.data)


class PurchaseRequestOffView(UpdateAPIView):
    serializer_class = PurchaseRequestOffSerializer
    http_method_names = ('patch',)

    def get_queryset(self):
        queryset = PurchaseRequest.objects.filter(
            is_active=True, user=self.request.user
        )
        return queryset


class PurchaseRequestAllOffView(APIView):
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        PurchaseRequest.objects.filter(user=self.request.user).update(
            is_active=False
        )
        return Response({'message': _('Все заявки очищены')}, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Offer.objects.filter(
            purchase_request__user=self.request.user,
            purchase_request__is_active=True
        ).select_related('purchase_request', 'purchase_request__user')


class AcceptedOffersListView(ListAPIView):
    serializer_class = AcceptedOfferListSerializer

    def get_queryset(self):
        queryset = (
            Offer.objects
            .filter(
                purchase_request__user=self.request.user,
                chat_room__is_accepted=True,
                chat_room__user=self.request.user,
            )
        )
        return queryset


class AcceptedOffersDeleteView(DestroyAPIView):

    def get_queryset(self):
        queryset = (
            Offer.objects
            .filter(
                purchase_request__user=self.request.user,
                chat_room__is_accepted=True,
                chat_room__user=self.request.user,
            )
        )
        return queryset

    def perform_destroy(self, offer):
        chat_room = offer.chat_room
        chat_room.is_accepted = False
        chat_room.save()


class AcceptedOffersDeleteAllView(APIView):
    http_method_names = ('delete',)

    def delete(self, request, *args, **kwargs):
        ChatRoom.objects.filter(
            user=self.request.user, is_accepted=True).update(is_accepted=False)
        return Response({'message': _('Все принятые предложения очищены')},
                        status=status.HTTP_204_NO_CONTENT)
