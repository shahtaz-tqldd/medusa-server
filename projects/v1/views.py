from rest_framework import generics, status, permissions

# helpers
from projects.v1 import res_msg
from base.helpers.response import APIResponse

# models
from projects.models import Project

# serializers
from projects.v1.serializers import (
    CreateProjectSerializer,
    ProjectDetailsSerializer,
)

class CreateNewProject(generics.CreateAPIView):
    """
    API view to create new project
    """
    RES_LANG = "en"
    serializer_class = CreateProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    """
    API view to get project list
    """
    RES_LANG = "en"
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectDetailsSerializer
    queryset = Project.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message=res_msg.PROJECT_LIST[self.RES_LANG],
        )
    

class ProjectDetails(generics.RetrieveAPIView):
    """
    API view to fetch project details
    """
    RES_LANG = "en"
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectDetailsSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message=res_msg.PROJECT_DETAILS[self.RES_LANG],
        )
    

class UpdateProjectDetails(generics.UpdateAPIView):
    """
    API view to update project details
    """
    RES_LANG = "en"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectDetailsSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return APIResponse.success(
            data=serializer.data,
            message=res_msg.PROJECT_UPDATED[self.RES_LANG],
            status=status.HTTP_205_RESET_CONTENT,
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
            status=status.HTTP_204_NO_CONTENT
        )
    