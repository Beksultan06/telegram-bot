import django_filters
import datetime
import pytz


from business.models import Service, ServiceCategory, ServiceSubCategory
from car.models import CarBrand
from info.models import Region


class ServiceCategoryFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains'
    )

    class Meta:
        model = ServiceCategory
        fields = ['title',]


class ServiceSubCategoryFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains'
    )

    class Meta:
        model = ServiceSubCategory
        fields = ['title', ]


class ServiceFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains'
    )
    categories = django_filters.ModelMultipleChoiceFilter(
        field_name='categories__id',
        queryset=ServiceCategory.objects.all(),
        to_field_name='id'
    )

    region = django_filters.ModelChoiceFilter(
        field_name='region', queryset=Region.objects.all()
    )

    class Meta:
        model = Service
        fields = ['category', 'sub_category', 'region', 'title', 'categories']


class StaticsServiceFilter(django_filters.FilterSet):
    created_from = django_filters.DateFilter(
        field_name='view_logs__created_at',
        input_formats=['%d.%m.%Y'],
        method='filter_created_from'
    )
    created_to = django_filters.DateTimeFilter(
        field_name='view_logs__created_at',
        input_formats=['%d.%m.%Y'],
        method='filter_created_to'
    )

    class Meta:
        model = Service
        fields = ['created_from', 'created_to']

    def filter_created_from(self, queryset, name, value):
        if value:
            value = datetime.datetime.combine(value, datetime.time.min)
            tz = pytz.timezone('Asia/Bishkek')
            value = tz.localize(value)
            return queryset.filter(view_logs__created_at__gte=value)
        return queryset

    def filter_created_to(self, queryset, name, value):
        if value:
            value = datetime.datetime.combine(value, datetime.time.max)
            tz = pytz.timezone('Asia/Bishkek')
            value = tz.localize(value)
            return queryset.filter(view_logs__created_at__lte=value)
        return queryset


class StaticsCarBrandFilter(django_filters.FilterSet):
    created_from = django_filters.DateFilter(
        field_name='car_models__purchase_request__created_at',
        input_formats=['%d.%m.%Y'],
        method='filter_created_from'
    )
    created_to = django_filters.DateTimeFilter(
        field_name='car_models__purchase_request__created_at',
        input_formats=['%d.%m.%Y'],
        method='filter_created_to'
    )

    class Meta:
        model = CarBrand
        fields = ['created_from', 'created_to']

    def filter_created_from(self, queryset, name, value):
        if value:
            value = datetime.datetime.combine(value, datetime.time.min)
            tz = pytz.timezone('Asia/Bishkek')
            value = tz.localize(value)
            return queryset.filter(car_models__purchase_request__created_at__gte=value)
        return queryset

    def filter_created_to(self, queryset, name, value):
        if value:
            value = datetime.datetime.combine(value, datetime.time.max)
            tz = pytz.timezone('Asia/Bishkek')
            value = tz.localize(value)
            return queryset.filter(car_models__purchase_request__created_at__lte=value)
        return queryset

