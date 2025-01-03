from info.models import PromotionalCodesAndDiscount

import django_filters


class PromotionalCodesAndDiscountFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains'
    )

    class Meta:
        model = PromotionalCodesAndDiscount
        fields = ['title', 'region']