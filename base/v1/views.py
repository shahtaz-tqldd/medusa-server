from django_filters.rest_framework import DjangoFilterBackend

# restframework utils
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter

# helpers
from base.v1 import res_msg
from base.helpers.pagination import CustomPagination
from base.helpers.filters import VisitorFilter, ClientFilter
from base.helpers.response import APIResponse

# models
from base.models import Visitor, Client

# serializers
from base.v1.serializers import (
    CreateVisitorSerializer, 
    VisitorSerializer,
    ClientSerializer,
    CreateClientSerializer,
)

class CreateOrUpdateVisitor(generics.CreateAPIView):
    """API view to create or update visitor details"""
    permission_classes = [permissions.AllowAny]
    serializer_class = CreateVisitorSerializer

    def post(self, request, *args, **kwargs):
        visitor_id = request.data.get("visitor_id")

        if visitor_id:
            try:
                visitor = Visitor.objects.get(id=visitor_id)
                visitor.update_visit()
                serializer = self.get_serializer(visitor)
                return APIResponse.success(
                    data={"visitor_id": str(visitor.id)},
                    message="Visitor updated successfully."
                )
            except Visitor.DoesNotExist:
                pass  # If visitor not found, we'll create a new one

        # If no visitor_id provided or invalid, create a new visitor
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        request.data['ip_address'] = ip

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse.success(
            data={"visitor_id": serializer.data["id"]},
            message="Visitor created successfully."
        )


class VisitorList(generics.ListAPIView):
    """API view to get visitor list"""
    RES_LANG = "en"
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VisitorFilter
    search_fields = ['city', 'country', 'device_name', 'device_type']
    ordering_fields = ['last_visit', 'visit_count']
    ordering = ['-last_visit']

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


class CreateClient(generics.CreateAPIView):
    """API View to create new client with project details"""  
    RES_LANG = 'en'
    permission_classes = [permissions.AllowAny]
    serializer_class = CreateClientSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['visitor_id'] = self.request.query_params.get('visitor_id')
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse.success(
            data=serializer.data,
            message=res_msg.CLIENT_CREATED[self.RES_LANG],
            status=status.HTTP_201_CREATED
        )
    

class  ClientList(generics.ListAPIView):
    """API view to get client list"""
    RES_LANG = "en"
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClientFilter
    search_fields = ['name', 'project_type', 'project_description']

    def get_queryset(self):
        queryset = Client.objects.all()
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
            message=res_msg.CLIENT_LIST[self.RES_LANG]
        )