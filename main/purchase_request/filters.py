import django_filters

from car.models import CarModel
from purchase_request.models import PurchaseRequest


class PurchaseRequestFilter(django_filters.FilterSet):
    model_in = django_filters.BaseInFilter(field_name='model__id')
    part_in = django_filters.BaseInFilter(field_name='part__id')

    class Meta:
        model = PurchaseRequest
        fields = ['id', 'part', 'region', 'model_in', 'part_in']

