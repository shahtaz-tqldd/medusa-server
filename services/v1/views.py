from django.db import transaction

from rest_framework import generics, permissions, status

# helpers
from services.v1 import res_msg
from base.helpers.response import APIResponse

# models
from services.models import Services, Skills

# serializers
from services.v1.serializer import (
    CreateServiceSerializer,
    ServiceDetailsSerializer,
    CreateSkillSerializer,
    SkillDetailsSerializer,
)
class CreateNewService(generics.CreateAPIView):
    """
    API View to create new service
    """
    RES_LANG = 'en'
    serializer_class = CreateServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = serializer.save()
        service_data = ServiceDetailsSerializer(service).data

        return APIResponse.success(
            data = service_data,
            message= res_msg.SERVICE_CREATED[self.RES_LANG],
            status=status.HTTP_201_CREATED
        )


class ServiceList(generics.ListAPIView):
    """
    API View to get service list
    """
    RES_LANG = 'en'
    serializer_class = ServiceDetailsSerializer
    queryset = Services.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return APIResponse.success(
            data=serializer.data, 
            message= res_msg.SERVICE_LIST[self.RES_LANG]
        )


class UpdateServiceDetails(generics.UpdateAPIView):
    """
    API View to update service details with id
    """
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceDetailsSerializer
    queryset = Services.objects.all()
    lookup_field = 'id'
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return APIResponse.success(
            data=serializer.data, 
            message= res_msg.SERVICE_UPDATED[self.RES_LANG],
            status=status.HTTP_205_RESET_CONTENT
        )
        
class DeleteService(generics.DestroyAPIView):
    """
    API View to delete service with id
    """
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    queryset = Services.objects.all()
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message= res_msg.SERVICE_DELETED[self.RES_LANG],
            status=status.HTTP_204_NO_CONTENT
        )


# -----------------
# SKILLS
# -----------------
class CreateNewSkills(generics.CreateAPIView):
    """
    API View to create new skills
    """
    RES_LANG = 'en'
    serializer_class = CreateSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        skills_data = request.data

        if not isinstance(skills_data, list):
            return APIResponse.error(message=res_msg.SKILL_LIST_EXPECTED[self.RES_LANG])

        serializer = CreateSkillSerializer(data=skills_data, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

        return APIResponse.success(
            data = serializer.data,
            message= f"{len(serializer.data)} {res_msg.SKILL_CREATED[self.RES_LANG]}",
            status=status.HTTP_201_CREATED
        )


class SkillList(generics.ListAPIView):
    """
    API View to get skill list
    """
    RES_LANG = 'en'
    serializer_class = SkillDetailsSerializer
    queryset = Skills.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return APIResponse.success(
            data=serializer.data, 
            message= res_msg.SKILL_LIST[self.RES_LANG]
        )


class UpdateSkillDetails(generics.UpdateAPIView):
    """
    API View to update Skill details with id
    """
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SkillDetailsSerializer
    queryset = Skills.objects.all()
    lookup_field = 'id'
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return APIResponse.success(
            data=serializer.data,
            message= res_msg.SKILL_UPDATED[self.RES_LANG],
            status=status.HTTP_205_RESET_CONTENT
        )

class DeleteSkill(generics.DestroyAPIView):
    """
    API View to delete Skill with id
    """
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    queryset = Skills.objects.all()
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message= res_msg.SKILL_DELETED[self.RES_LANG],
            status=status.HTTP_204_NO_CONTENT
        )