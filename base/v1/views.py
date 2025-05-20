from django_filters.rest_framework import DjangoFilterBackend

# restframework utils
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny

# helpers
from base.v1 import res_msg
from base.helpers.pagination import CustomPagination
from base.helpers.visitor_filter import VisitorFilter
from base.helpers.response import APIResponse

# models
from base.models import Visitor

# serializers
from base.v1.serializers import CreateVisitorSerializer, VisitorSerializer


class CreateVisitor(generics.CreateAPIView):
    """
    API view to store visitor details
    """
    permission_class = [AllowAny]
    serializer_class = CreateVisitorSerializer
    RES_LANG = 'en'
    
    def create(self, request, *args, **kwargs):
        # Extract client IP if not provided in data
        if 'ip_address' not in request.data:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            request.data['ip_address'] = ip
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return APIResponse.success(message=res_msg.VISITOR_CREATED[self.RES_LANG])


class VisitorList(generics.ListAPIView):
    """
    API view to get visitor list
    """
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VisitorFilter
    search_fields = ['city', 'country', 'device_name', 'device_type']
    ordering_fields = ['last_visit', 'visit_count']
    ordering = ['-last_visit']
    RES_LANG = "en"

    def get_queryset(self):
        queryset = Visitor.objects.all()
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        
        return APIResponse.success(
            data=data, 
            message=res_msg.VISITOR_LIST[self.RES_LANG]
        )
