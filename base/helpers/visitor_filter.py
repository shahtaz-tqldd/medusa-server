from django_filters.rest_framework import FilterSet, CharFilter, DateFromToRangeFilter
from base.models import Visitor

class VisitorFilter(FilterSet):
    """
    Filter for blogs with various options
    """
    visit_from = DateFromToRangeFilter(field_name='last_visit')
    
    class Meta:
        model = Visitor
        fields = ['city', 'country', 'device_name', 'device_type', 'visit_from']
        