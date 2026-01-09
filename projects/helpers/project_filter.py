from django_filters.rest_framework import FilterSet, CharFilter
from projects.models import Project

class ProjectFilter(FilterSet):
    """Filter for blogs with various options"""
    type = CharFilter(field_name='type')
    
    class Meta:
        model = Project
        fields = ['type']
        