from datetime import timedelta

from django.db.models import Q, Prefetch, Max
from django.db.models.functions import Greatest
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, RetrieveAPIView
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from business.models import Business
from business.permissions import IsBusinessPermission
from car.models import CarBrand
from car.serializers import CarModelSerializer
from chat.paginators import RequestPagination
from purchase_request.filters import PurchaseRequestFilter
from purchase_request.models import PurchaseRequest, Offer
from purchase_request.serializers import (
    PurchaseRequestForBusinessListSerializer, OfferCreateSerializer,
    OfferUpdateSerializer,
    AcceptedPurchaseRequestForBusinessListSerializer, OfferDetailSerializer,
)
from purchase_request.views import PurchaseRequestDetailView


class PurchaseRequestForBusinessListView(ListAPIView):
    serializer_class = PurchaseRequestForBusinessListSerializer
    permission_classes = [IsAuthenticated, IsBusinessPermission, ]
    filterset_class = PurchaseRequestFilter

    # pagination_class = RequestPagination

    def get_queryset(self):
        business = self.request.user.business
        last_day = timezone.now() - timedelta(days=1)
        queryset = PurchaseRequest.objects.filter(is_active=True).filter(created_at__gt=last_day)
        business_parts = business.common_parts.all()
        car_brands = self.request.user.business.car_brands.all()
        if business.types_of_purchase_requests == business.by_common_parts:
            queryset = queryset.filter(part__in=business_parts)
        elif business.types_of_purchase_requests == business.by_car_brands:
            queryset = queryset.filter(model__brand__in=car_brands)
        else:
            queryset = queryset.filter(
                Q(part__in=business_parts) |
                Q(model__brand__in=car_brands)
            )

        queryset.select_related('model__brand', 'part', 'user', )
        queryset.prefetch_related(
            'offers', 'offers__images', 'offers__business'
        )
        return queryset


class Api2PurchaseRequestForBusinessListView(PurchaseRequestForBusinessListView):
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        business = user.business
        queryset = PurchaseRequest.objects.filter(is_active=True)
        if not user.is_staff:
            queryset = queryset.filter(Q(type__cost__lte=0) | Q(type=None))
            business_parts = business.common_parts.all()
            car_brands = self.request.user.business.car_brands.all()
            if business.types_of_purchase_requests == business.by_common_parts:
                queryset = queryset.filter(part__in=business_parts)
            elif business.types_of_purchase_requests == business.by_car_brands:
                queryset = queryset.filter(model__brand__in=car_brands)
            else:
                queryset = queryset.filter(
                    Q(part__in=business_parts) |
                    Q(model__brand__in=car_brands)
                )
        if user.is_staff:
            queryset = queryset.filter(type__cost__gt=0).distinct()

        queryset.select_related('model__brand', 'part', 'user', )
        queryset.prefetch_related(
            'offers', 'offers__images', 'offers__business'
        )
        return queryset


class Api2BusinessCarModelListView(ListAPIView):
    serializer_class = CarModelSerializer
    permission_classes = [IsAuthenticated, IsBusinessPermission, ]

    def get_queryset(self):
        business = self.request.user.business

        # Предварительно загружаем бренды автомобилей и их модели для текущего бизнеса
        business_with_brands_and_models = Business.objects.filter(pk=business.pk).prefetch_related(
            Prefetch(
                'car_brands',
                queryset=CarBrand.objects.prefetch_related('car_models')
            )
        ).first()
        car_models = []

        # Проверяем, что бизнес был найден
        if business_with_brands_and_models:
            # Проходим по всем брендам, связанным с бизнесом
            for brand in business_with_brands_and_models.car_brands.all():
                # Добавляем все модели автомобилей текущего бренда в общий список
                car_models.extend(brand.car_models.all())

        return car_models


class Api2PurchaseRequestForBusinessDetailView(RetrieveAPIView):
    model = PurchaseRequest
    serializer_class = PurchaseRequestForBusinessListSerializer
    permission_classes = [IsAuthenticated, IsBusinessPermission]

    def get_queryset(self):
        # business = self.request.user.business
        queryset = PurchaseRequest.objects.filter(is_active=True)
        # business_parts = business.common_parts.all()
        # car_brands = self.request.user.business.car_brands.all()
        # if business.types_of_purchase_requests == business.by_common_parts:
        #     queryset = queryset.filter(part__in=business_parts)
        # elif business.types_of_purchase_requests == business.by_car_brands:
        #     queryset = queryset.filter(model__brand__in=car_brands)
        # else:
        #     queryset = queryset.filter(
        #         Q(part__in=business_parts) |
        #         Q(model__brand__in=car_brands)
        #     )
        #
        # queryset.select_related('model__brand', 'part', 'user', )
        # queryset.prefetch_related(
        #     'offers', 'offers__images', 'offers__business'
        # )
        return queryset


class Api2PurchaseRequestIsViewedView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessPermission, ]

    def post(self, request):
        p_request = get_object_or_404(PurchaseRequest, pk=request.data['pk'])
        p_request.viewed_users.add(request.user)
        return Response({'status': 'marked as viewed'}, status=status.HTTP_200_OK)


class AcceptedPurchaseRequestForBusinessListView(ListAPIView):
    serializer_class = AcceptedPurchaseRequestForBusinessListSerializer
    permission_classes = [IsAuthenticated, IsBusinessPermission, ]
    queryset = PurchaseRequest.objects.all()

    def get_queryset(self):
        business = self.request.user.business
        queryset = (
            PurchaseRequest.objects.
            filter(chat_rooms__isnull=False, chat_rooms__business=business)
            .annotate(
                latest_offer_date=Max('offers__created_at'),
                latest_message_date=Max('chat_rooms__messages__created_at')
            )
            .annotate(
                latest_activity_date=Greatest('latest_offer_date', 'latest_message_date')
            )
            .select_related('model', 'part', 'user', 'user__business')
            .prefetch_related('offers', 'offers__images', 'offers__business')
            .order_by('-latest_activity_date')
        )

        return queryset


class DeleteAllAcceptedPurchaseRequestForBusinessView(APIView):
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        business = self.request.user.business
        Offer.objects.filter(
            business=business, chat_room__is_accepted=True).delete()
        return Response(
            {'message': _('Все принятые заявки очищены')}, status=status.HTTP_200_OK
        )


class OfferCreateView(CreateAPIView):
    serializer_class = OfferCreateSerializer
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsBusinessPermission, ]

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)


class OfferDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsBusinessPermission, ]
    http_method_names = ('patch', 'get', 'delete')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferDetailSerializer
        return OfferUpdateSerializer

    def get_queryset(self):
        business = self.request.user.business
        return Offer.objects.filter(business=business)


class OfferConditionsListView(APIView):
    def get(self, *args, **kwargs):
        conditions = [
            {"value": data[0], "title": data[1]}
            for data in Offer.CONDITIONS
        ]
        return Response(conditions, status=status.HTTP_200_OK)


class OfferAvailabilityListView(APIView):
    def get(self, *args, **kwargs):
        availabilities = [
            {"value": data[0], "title": data[1]}
            for data in Offer.AVAILABILITIES
        ]
        return Response(availabilities, status=status.HTTP_200_OK)


class OfferDifferenceListView(APIView):
    def get(self, *args, **kwargs):
        differences = [
            {"value": data[0], "title": data[1]}
            for data in Offer.DIFFERENCES
        ]
        return Response(differences, status=status.HTTP_200_OK)
