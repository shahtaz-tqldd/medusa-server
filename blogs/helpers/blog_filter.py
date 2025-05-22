from django_filters.rest_framework import FilterSet, CharFilter, DateFromToRangeFilter
from blogs.models import Blog

class BlogFilter(FilterSet):
    """Filter for blogs with various options"""
    category = CharFilter(field_name='category__name')
    tag = CharFilter(field_name='tags__name')
    published_from = DateFromToRangeFilter(field_name='published_at')
    
    class Meta:
        model = Blog
        fields = ['category', 'tag', 'published_from', 'status']
        