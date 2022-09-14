import django_filters
from django_filters import rest_framework as filters

from bills.bills_parser.models import Bill


class BillFilter(filters.FilterSet):
    client_name__name = django_filters.CharFilter(field_name='client_name__name', lookup_expr='exact')
    client_org__name = django_filters.CharFilter(field_name='client_org__name', lookup_expr='exact')

    class Meta:
        model = Bill
        fields = ['client_name', 'client_org']
