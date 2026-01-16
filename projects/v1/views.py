from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter


# helpers
from projects.v1 import res_msg
from base.helpers.response import APIResponse
from base.helpers.pagination import CustomPagination
from projects.helpers.project_filter import ProjectFilter
# models
from projects.models import Project

# serializers
from projects.v1.serializers import (
    CreateProjectSerializer,
    ProjectDetailsSerializer,
    ProjectBasicDetailsSerializer,
    UpdateProjectSerializer
)

class CreateNewProject(generics.CreateAPIView):
    """
    API view to create new project
    """
    RES_LANG = "en"
    serializer_class = CreateProjectSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        project_data = ProjectDetailsSerializer(project).data

        return APIResponse.success(
            data=project_data,
            message=res_msg.PROJECT_CREATED[self.RES_LANG],
            status=status.HTTP_201_CREATED
        )


class ProjectList(generics.ListAPIView):
    """API View to get blog list with pagination, filtering and search"""
    serializer_class = ProjectBasicDetailsSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    RES_LANG = "en"
    
    def get_queryset(self):
        # By default, only show published projects
        queryset = Project.objects.all()
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
            message=res_msg.PROJECT_LIST[self.RES_LANG]
        )


class ProjectDetails(generics.RetrieveAPIView):
    """
    API view to fetch project details
    """
    RES_LANG = "en"
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectDetailsSerializer
    queryset = Project.objects.all()
    lookup_field = "id"

    def _is_admin_view(self):
        """
        Check if admin_view=true is passed in query params
        """
        admin_view = self.request.query_params.get("admin_view", "").lower()
        return admin_view in ("true", "1", "yes")

    def get_object(self):
        lookup_value = self.kwargs.get("id")

        try:
            project = self.get_queryset().get(id=lookup_value)

            # Increment view count only for non-admin views
            if not self._is_admin_view():
                Project.objects.filter(id=lookup_value).update(
                    view_count=F("view_count") + 1
                )

            return project

        except Project.DoesNotExist:
            raise NotFound(
                detail=res_msg.PROJECT_NOT_FOUND[self.RES_LANG]
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return APIResponse.success(
            data=serializer.data,
            message=res_msg.PROJECT_DETAILS[self.RES_LANG],
        )

    

class UpdateProject(generics.UpdateAPIView):
    """
    API view to update an existing project
    """
    RES_LANG = "en"
    serializer_class = UpdateProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Project.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        project_data = ProjectDetailsSerializer(project).data

        return APIResponse.success(
            data=project_data,
            message=res_msg.PROJECT_UPDATED[self.RES_LANG],
            status=status.HTTP_200_OK,
        )


class DeleteProject(generics.DestroyAPIView):
    """
    API view to delete project
    """
    RES_LANG = "en"
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            message=res_msg.PROJECT_DELETED[self.RES_LANG],
            status=status.HTTP_200_OK
        )
    