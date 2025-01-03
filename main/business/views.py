from django.db.models import Count, Q, OuterRef, Subquery
from rest_framework.generics import (
    ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView,
    ListCreateAPIView, UpdateAPIView, get_object_or_404
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import IntegrityError, transaction

from business.filters import (
    ServiceFilter, ServiceCategoryFilter, ServiceSubCategoryFilter,
    StaticsServiceFilter, StaticsCarBrandFilter
)
from business.models import (
    Tariff, Business, Service, ServiceCategory, ServiceSubCategory,
    ServiceViewLog, PayboxOrder, PayboxPaymentTransaction
)
from business.permissions import IsBusinessPermission
from business.serializers import (
    TariffSerializer, BusinessSerializer, ServiceSerializer,
    ServiceCategorySerializer, ServiceSubCategorySerializer,
    TariffChangeSerializer, BusinessCarBrandSerializer,
    BusinessDeactivateSerializer, BusinessCommonParsSerializer,
    BusinessActivateSerializer, ServiceViewLogCreateSerializer,
    ServiceDetailSerializer, PayboxOrderSerializer, StaticsCarBrandSerializer,
    StaticsServiceSerializer, CategoryServiceViewLogSerializer, Api2BusinessSerializer,
    Api2ServiceViewLogCreateSerializer,
)
from car.models import CarBrand, Part
from car.serializers import CarBrandForBusinessSerializer, CommonPartForBusinessSerializer, MyCarBrandsSerializer


class TariffListView(ListAPIView):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = (IsAuthenticated, IsBusinessPermission,)


class ChangeTariffView(UpdateAPIView):
    serializer_class = TariffChangeSerializer
    permission_classes = (IsAuthenticated, IsBusinessPermission,)
    http_method_names = ('patch',)

    def get_object(self):
        return Business.objects.filter(user=self.request.user).first()


class BusinessCreateView(CreateAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class Api2BusinessCreateView(CreateAPIView):
    queryset = Business.objects.all()
    serializer_class = Api2BusinessSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BusinessDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = (IsAuthenticated, IsBusinessPermission,)

    def get_object(self):
        return self.queryset.filter(user=self.request.user).first()


class ServiceCategoryListView(ListAPIView):
    serializer_class = ServiceCategorySerializer
    filterset_class = ServiceCategoryFilter

    def get_queryset(self):
        return ServiceCategory.objects.prefetch_related(
            'services', 'sub_categories'
        )


class ServiceSubCategoryListView(ListAPIView):
    serializer_class = ServiceSubCategorySerializer
    filterset_class = ServiceSubCategoryFilter

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return ServiceSubCategory.objects.filter(category_id=category_id)


class Api2ServiceSubCategoryListView(ServiceSubCategoryListView):
    pagination_class = LimitOffsetPagination


class ServiceListView(ListAPIView):
    serializer_class = ServiceSerializer
    filterset_class = ServiceFilter
    queryset = Service.objects.all()


class Api2ServiceListView(ServiceListView):
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset().distinct()
        categories = self.request.query_params.getlist('categories')
        category = self.request.query_params.get('category')

        categories_ids = queryset.filter(categories__in=categories).values_list('id', flat=True) if categories else []
        category_ids = queryset.filter(category=category).values_list('id', flat=True) if category else []

        combined_ids = set(categories_ids) | set(category_ids)
        if combined_ids:
            queryset = queryset.filter(id__in=combined_ids)
        else:
            queryset = queryset.filter(category_id=category)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        title = request.query_params.get('title')
        region = request.query_params.get('region')
        queryset = queryset.filter(title__icontains=title) if title else queryset
        queryset = queryset.filter(region__id=region) if region else queryset

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

            # If not paginated, serialize the whole queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceViewLogCreate(CreateAPIView):
    serializer_class = ServiceViewLogCreateSerializer
    queryset = ServiceViewLog.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid(raise_exception=False)
        if is_valid:
            serializer.save(user=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"success": True}, status=status.HTTP_200_OK, headers=headers
        )


class Api2ServiceViewLogCreate(CreateAPIView):
    serializer_class = Api2ServiceViewLogCreateSerializer
    queryset = ServiceViewLog.objects.all()

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid(raise_exception=False)
        if is_valid:
            serializer.save(user=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"success": True}, status=status.HTTP_200_OK, headers=headers
        )


class BusinessServiceListCreateView(ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsBusinessPermission]

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        return Service.objects.filter(business__user=self.request.user)


class BusinessServiceDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    permission_classes = (IsAuthenticated, IsBusinessPermission)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceDetailSerializer
        return ServiceSerializer

    def get_queryset(self):
        return Service.objects.filter(business__user=self.request.user)


class BusinessCarBrandsUpdateView(UpdateAPIView):
    serializer_class = BusinessCarBrandSerializer
    http_method_names = ['put', 'patch']
    permission_classes = (IsAuthenticated, IsBusinessPermission,)

    def get_object(self):
        return self.request.user.business


class MyCarBrandsListView(ListAPIView):
    serializer_class = MyCarBrandsSerializer
    queryset = CarBrand.objects.all()
    permission_classes = (IsAuthenticated, IsBusinessPermission,)

    def get_queryset(self):
        queryset = CarBrand.objects.filter(businesses__user=self.request.user)
        return queryset


class BusinessCarBrandsListView(ListAPIView):
    serializer_class = CarBrandForBusinessSerializer
    queryset = CarBrand.objects.all()
    permission_classes = (IsAuthenticated, IsBusinessPermission,)
    filterset_fields = ("category",)


class BusinessCommonPartsUpdateView(UpdateAPIView):
    serializer_class = BusinessCommonParsSerializer
    http_method_names = ['patch']
    permission_classes = (IsAuthenticated, IsBusinessPermission,)

    def get_object(self):
        return self.request.user.business


class BusinessCommonPartsListView(ListAPIView):
    serializer_class = CommonPartForBusinessSerializer
    queryset = Part.objects.filter(category__is_common_parts=True)
    permission_classes = (IsAuthenticated, IsBusinessPermission,)


class BusinessActivateView(UpdateAPIView):
    serializer_class = BusinessActivateSerializer
    queryset = Business.objects.filter(is_active=False)
    http_method_names = ['patch', ]

    def get_object(self):
        return get_object_or_404(
            queryset=self.queryset, user=self.request.user
        )


class BusinessDeactivateView(UpdateAPIView):
    serializer_class = BusinessDeactivateSerializer
    queryset = Business.objects.filter(is_active=True)
    http_method_names = ['patch', ]
    permission_classes = (IsAuthenticated, IsBusinessPermission,)

    def get_object(self):
        return self.queryset.filter(user=self.request.user).first()


class BusinessPurchaseRequestTypesView(APIView):
    def get(self, *args, **kwargs):
        engines = [
            {"value": data[0], "title": data[1]}
            for data in Business.TYPES_OF_PURCHASE_REQUESTS
        ]
        return Response(engines, status=status.HTTP_200_OK)


class PayboxOrderCreateView(CreateAPIView):
    serializer_class = PayboxOrderSerializer
    queryset = PayboxOrder.objects.all()
    permission_classes = (IsAuthenticated, IsBusinessPermission)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)


class PayboxTransactionResultView(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        data = request.data
        result = data.get('pg_result')
        transaction_id = data.get('pg_order_id')
        amount = float(data.get('pg_amount').replace(',', '.'))

        paybox_payment_id = data.get('pg_payment_id')
        try:
            paybox_transaction = PayboxPaymentTransaction.objects.create(
                id=paybox_payment_id
            )
        except IntegrityError:
            return Response("Payment already", status=status.HTTP_200_OK)

        paybox_order = PayboxOrder.objects.get(pk=transaction_id)
        paybox_order.paybox_payment = paybox_transaction

        paybox_order.amount = amount
        if int(result) == 1:
            paybox_order.status = PayboxOrder.SUCCESS
            Business.increase_balance(
                business_id=paybox_order.business_id,
                amount=amount
            )
        else:
            error_description = data.get('pg_failure_description')
            if error_description:
                paybox_order.description += '\nОшибка: ' + error_description
            paybox_order.status = PayboxOrder.FAILED
        paybox_order.save()
        return Response(status=status.HTTP_200_OK)


class StaticsCarBrandView(ListAPIView):
    permission_classes = (IsAuthenticated, IsBusinessPermission)
    filterset_class = StaticsCarBrandFilter
    serializer_class = StaticsCarBrandSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            request_subquery = CarBrand.objects.filter(
                pk=OuterRef('pk')
            ).annotate(
                request_count=Count('car_models__purchase_request')
            ).values('request_count')

            offer_subquery = CarBrand.objects.filter(
                pk=OuterRef('pk')
            ).annotate(
                offer_count=Count('car_models__purchase_request__offers')
            ).values('offer_count')

            return (
                CarBrand.objects.annotate(
                    request_count=Subquery(request_subquery[:1]),
                    offer_count=Subquery(offer_subquery[:1])
                )
            )

        user_car_brands = self.request.user.business.car_brands.values_list('pk', flat=True)

        request_subquery = CarBrand.objects.filter(
            pk=OuterRef('pk')
        ).annotate(
            request_count=Count('car_models__purchase_request')
        ).values('request_count')

        offer_subquery = CarBrand.objects.filter(
            pk=OuterRef('pk')
        ).annotate(
            offer_count=Count('car_models__purchase_request__offers')
        ).values('offer_count')

        return (
            CarBrand.objects.filter(pk__in=user_car_brands)
            .annotate(
                request_count=Subquery(request_subquery[:1]),
                offer_count=Subquery(offer_subquery[:1])
            )
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StaticsServiceView(ListAPIView):
    permission_classes = (IsAuthenticated, IsBusinessPermission)
    filterset_class = StaticsServiceFilter
    serializer_class = StaticsServiceSerializer

    def get_queryset(self):
        queryset = (
            Service.objects
            .annotate(
                view_count=Count('view_logs')
            )
        )
        if self.request.user.is_superuser:
            return queryset
        queryset = queryset.filter(business=self.request.user.business)
        return queryset

    def get_just_queryset(self):
        queryset = (
            Service.objects
            .filter(business=self.request.user.business)
        )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        exclude_queryset = (
            self.get_just_queryset()
            .exclude(pk__in=queryset.values_list('pk', flat=True))
        )
        full_queryset = list(queryset) + list(exclude_queryset)
        serializer = self.get_serializer(full_queryset, many=True)
        return Response(serializer.data)


class ServiceViewLogsByCategory(APIView):
    def get(self, request, *args, **kwargs):
        categories = ServiceCategory.objects.all()
        result = []

        for category in categories:
            services = Service.objects.filter(Q(categories=category) | Q(category=category)).distinct().filter(
                business=self.request.user.business)

            services_data = []
            for service in services:
                view_count = ServiceViewLog.objects.filter(service=service, category=category).count()
                services_data.append({
                    'service_id': service.id,
                    'service_title': service.title,
                    'address': service.address,
                    'image': service.image,
                    'view_count': view_count
                })

            if services_data:
                result.append({
                    'category_id': category.id,
                    'category_name': category.title,
                    'services': services_data
                })

        serializer = CategoryServiceViewLogSerializer(result, many=True)
        return Response(serializer.data)
