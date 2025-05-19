import random

from rest_framework import generics, permissions
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_205_RESET_CONTENT,
    HTTP_404_NOT_FOUND,
)

from base.helpers.response import APIResponse

from projects.models import Project, ProjectImage
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
    APIView to create New project
    """
    RESPONSE_LANGUAGE = "en"
    serializer_class = CreateProjectSerializer
    serializer_class = CreateProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.save()
        project_data = ProjectDetailsSerializer(project).data

        return APIResponse.success(
            data = project_data, 
            message = PROJECT_CREATED[self.RESPONSE_LANGUAGE], 
            status = HTTP_201_CREATED
        )


class ProjectList(generics.ListAPIView):
    """
    API view to get project list
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectDetailsSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return APIResponse.success(
            data = serializer.validated_data,
            message = PROJECT_LIST[self.RESPONSE_LANGUAGE],
        )


class ProjectDetails(generics.RetrieveAPIView):
    """
    API View to fetch proejct details
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectDetailsSerializer

    def retrieve(self, request):
        serializer = self.get_serializer()

        return APIResponse.success(
            data=serializer.data, 
            message = PROJECT_DETAILS[self.RESPONSE_LANGUAGE], 
        )


class UpdateProjectDetails(generics.UpdateAPIView):
    """
    API view to update proejct details
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectDetailsSerializer

    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return APIResponse.success(
            data=serializer.data,
            message = PROJECT_UPDATED[self.RESPONSE_LANGUAGE], 
            status=HTTP_205_RESET_CONTENT,
        )


class DeleteProject(generics.DestroyAPIView):
    """
    API view to delete project
    """
    RESPONSE_LANGUAGE = "en"
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request):
        return APIResponse.success(message = PROJECT_DELETED[self.RESPONSE_LANGUAGE])

