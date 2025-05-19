from rest_framework import generics, permissions
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_205_RESET_CONTENT,
    HTTP_204_NO_CONTENT,
)

from base.helpers.response import APIResponse

from projects.models import Project
from projects.v1.serializers import (
    CreateProjectSerializer,
    ProjectDetailsSerializer,
)

from projects.v1.res_msg import (
    PROJECT_CREATED,
    PROJECT_LIST,
    PROJECT_DETAILS,
    PROJECT_UPDATED,
    PROJECT_DELETED,
)


class CreateNewProject(generics.CreateAPIView):
    """
    API view to create new project
    """
    RESPONSE_LANGUAGE = "en"
    serializer_class = CreateProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        project_data = ProjectDetailsSerializer(project).data

        return APIResponse.success(
            data=project_data,
            message=PROJECT_CREATED[self.RESPONSE_LANGUAGE],
            status=HTTP_201_CREATED
        )


class ProjectList(generics.ListAPIView):
    """
    API view to get project list
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectDetailsSerializer
    queryset = Project.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message=PROJECT_LIST[self.RESPONSE_LANGUAGE],
        )
    

class ProjectDetails(generics.RetrieveAPIView):
    """
    API view to fetch project details
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectDetailsSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message=PROJECT_DETAILS[self.RESPONSE_LANGUAGE],
        )
    

class UpdateProjectDetails(generics.UpdateAPIView):
    """
    API view to update project details
    """
    RESPONSE_LANGUAGE = "en"
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
            message=PROJECT_UPDATED[self.RESPONSE_LANGUAGE],
            status=HTTP_205_RESET_CONTENT,
        )


class DeleteProject(generics.DestroyAPIView):
    """
    API view to delete project
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            message=PROJECT_DELETED[self.RESPONSE_LANGUAGE],
            status=HTTP_204_NO_CONTENT
        )
    