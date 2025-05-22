from django_filters.rest_framework import FilterSet, CharFilter, DateFromToRangeFilter
from base.models import Visitor, Client

class VisitorFilter(FilterSet):
    """Filter for visitor with various options"""
    visit_from = DateFromToRangeFilter(field_name='last_visit')
    
    class Meta:
        model = Visitor
        fields = ['city', 'country', 'device_name', 'device_type', 'visit_from']


class ClientFilter(FilterSet):
    """Filter for client with various options"""
    visitor_country = CharFilter(field_name='visitor__country')
    visit_from = DateFromToRangeFilter(field_name='visitor__last_visit')
    class Meta:
        model = Client
        fields = ['project_type', 'design_required', 'visitor_country', 'visit_from']
        