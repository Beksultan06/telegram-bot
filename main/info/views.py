from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from info.filters import PromotionalCodesAndDiscountFilter
from info.models import (
    Region, PromotionalCodesAndDiscount, Banner, AboutApp, Support, VersionControl
)
from info.serializers import (
    RegionSerializer, PromotionalCodesAndDiscountSerializer,
    BannerListSerializer, BannerDetailSerializer, AboutAppSerializer,
    SupportSerializer, AdPageSerializer, AndroidVersionControlSerializer, IOSVersionControlSerializer
)


class RegionListView(ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class PromotionalCodesAndDiscountListView(ListAPIView):
    queryset = PromotionalCodesAndDiscount.objects.all()
    serializer_class = PromotionalCodesAndDiscountSerializer
    filterset_class = PromotionalCodesAndDiscountFilter


class PromotionalCodesAndDiscounDetailView(RetrieveAPIView):
    queryset = PromotionalCodesAndDiscount.objects.filter(is_active=True)
    serializer_class = PromotionalCodesAndDiscountSerializer

    def get(self, request, *args, **kwargs):

        queryset = self.get_object()
        user_id = request.user.id
        # Вызываем метод для инкрементации кликов
        queryset.increment_click_count(user_id)

        return self.retrieve(request, *args, **kwargs)

class BannerListView(ListAPIView):
    queryset = Banner.objects.filter(is_active=True).order_by('?')
    serializer_class = BannerListSerializer


class BannerDetailView(RetrieveAPIView):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerDetailSerializer

    def get(self, request, *args, **kwargs):

        banner = self.get_object()
        user_id = request.user.id
        # Вызываем метод для инкрементации кликов
        banner.increment_click_count(user_id)

        return self.retrieve(request, *args, **kwargs)

class SupportFAQView(RetrieveAPIView):
    serializer_class = SupportSerializer

    def get_object(self):
        return Support.objects.first()


class AboutAppView(RetrieveAPIView):
    serializer_class = AboutAppSerializer

    def get_object(self):
        return AboutApp.objects.first()


class AdPageView(RetrieveAPIView):
    serializer_class = AdPageSerializer
    http_method_names = ('get',)

    def get_object(self):
        return Support.objects.first()


class AndroidVersionControlAPIView(RetrieveAPIView):
    serializer_class = AndroidVersionControlSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return VersionControl.objects.first()


class IOSVersionControlAPIView(RetrieveAPIView):
    serializer_class = IOSVersionControlSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return VersionControl.objects.first()
