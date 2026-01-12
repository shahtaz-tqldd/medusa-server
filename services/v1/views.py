import logging
from rest_framework import generics, permissions, status
from base.managers.cloudinary import CloudinaryImageManager

# helpers
from services.v1 import res_msg
from base.helpers.response import APIResponse

# models
from services.models import (
    Services, 
    SkillsAndIntroduction, 
    Experience,
    Achievement
)

# serializers
from services.v1.serializer import (
    CreateServiceSerializer,
    ServiceDetailsSerializer,
    SkillsDetailsSerializer,
    CreateExperienceSerializer,
    ExperienceDetailsSerializer,
    CreateAchievementSerializer,
    AchievementDetailsSerializer
)

logger = logging.getLogger(__name__)

# -----------------
# SERVICE
# -----------------
class CreateNewService(generics.CreateAPIView):
    """API View to create new service"""
    RES_LANG = 'en'
    serializer_class = CreateServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = serializer.save()
        service_data = ServiceDetailsSerializer(service).data

        return APIResponse.success(
            data=service_data,
            message=res_msg.SERVICE_CREATED[self.RES_LANG],
            status=status.HTTP_201_CREATED
        )


class ServiceDetails(generics.RetrieveAPIView):
    """API View to get service details"""
    RES_LANG = "en"
    serializer_class = ServiceDetailsSerializer
    queryset = Services.objects.all()
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return APIResponse.success(
            data=serializer.data,
            message=res_msg.SERVICE_DETAILS[self.RES_LANG],
        )

class ServiceList(generics.ListAPIView):
    """API View to get service list"""
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

class UpdateService(generics.UpdateAPIView):
    """API View to update existing service"""
    RES_LANG = 'en'
    serializer_class = CreateServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Services.objects.all()
    
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_public_id = instance.featured_image_public_id
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # If new image is uploaded and old one exists, delete old image
        if 'featured_image' in request.FILES and old_public_id:
            try:
                image_manager = CloudinaryImageManager()
                image_manager.delete(old_public_id)
            except Exception as e:
                logger.warning(f"Failed to delete old image: {e}")
        
        service = serializer.save()
        service_data = ServiceDetailsSerializer(service).data

        return APIResponse.success(
            data=service_data,
            message=res_msg.SERVICE_UPDATED[self.RES_LANG],
            status=status.HTTP_200_OK
        )

class DeleteService(generics.DestroyAPIView):
    """API View to delete service with id"""
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    queryset = Services.objects.all()
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message= res_msg.SERVICE_DELETED[self.RES_LANG],
            status=status.HTTP_200_OK
        )


# -----------------
# SKILLS AND INTRODUCTION
# -----------------
class SkillDetailsView(generics.RetrieveAPIView):
    """API View to get skills and introduction details"""
    RES_LANG = "en"
    serializer_class = SkillsDetailsSerializer

    def get_object(self):
        instance = SkillsAndIntroduction.objects.first()
        if not instance:
            return None
        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = SkillsAndIntroduction.objects.first()
        if not instance:
            return APIResponse.success(
                data=None,
                message=res_msg.SKILL_NOT_FOUND[self.RES_LANG],
            )
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message=res_msg.SKILL_DETAILS[self.RES_LANG],
        )
   
class UpdateSkillDetails(generics.UpdateAPIView):
    """API View to update skill details (partial update)"""
    RES_LANG = "en"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SkillsDetailsSerializer
    http_method_names = ["patch"]

    def get_object(self):
        instance = SkillsAndIntroduction.objects.first()

        if not instance:
            instance = SkillsAndIntroduction.objects.create(
                title="",
                expertise="",
                my_story="",
                key_focus_areas=[],
                language_and_frameworks=[],
                tools_and_database=[],
                other_competency=[]
            )

        return instance

    def patch(self, request, *args, **kwargs):
        print(request.data)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse.success(
            data=serializer.data,
            message=res_msg.SKILL_UPDATED[self.RES_LANG],
            status=status.HTTP_200_OK
        )


# -----------------
# WORK EXPERIENCES
# -----------------
class CreateNewExperience(generics.CreateAPIView):
    """API View to create new experience"""
    RES_LANG = 'en'
    serializer_class = CreateExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse.success(
            data = serializer.data,
            message=res_msg.EXPERIENCE_CREATED[self.RES_LANG],
            status=status.HTTP_201_CREATED
        )

class ExperienceList(generics.ListAPIView):
    """API View to get experience list"""
    RES_LANG = 'en'
    serializer_class = ExperienceDetailsSerializer
    queryset = Experience.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return APIResponse.success(
            data=serializer.data, 
            message= res_msg.EXPERIENCE_LIST[self.RES_LANG]
        )

class UpdateExperienceDetails(generics.UpdateAPIView):
    """API View to update Experience details with id"""
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExperienceDetailsSerializer
    queryset = Experience.objects.all()
    lookup_field = 'id'
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return APIResponse.success(
            data=serializer.data,
            message= res_msg.EXPERIENCE_UPDATED[self.RES_LANG],
            status=status.HTTP_205_RESET_CONTENT
        )

class DeleteExperience(generics.DestroyAPIView):
    """API View to delete Experience with id"""
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    queryset = Experience.objects.all()
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message= res_msg.EXPERIENCE_DELETED[self.RES_LANG],
            status=status.HTTP_200_OK
        )
    

# -----------------
# ACHIEVEMENTS
# -----------------
class CreateAchievement(generics.CreateAPIView):
    """API View to create new acheivement"""
    RES_LANG = 'en'
    serializer_class = CreateAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return APIResponse.success(
                data = serializer.data,
                message=res_msg.ACHIEVEMENT_CREATED[self.RES_LANG],
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Failed to create achievement: {e}")
            return APIResponse.error(
                message=f"Failed to create: {e}"
            )


class AchievementList(generics.ListAPIView):
    """API View to get achievement list"""
    RES_LANG = 'en'
    serializer_class = AchievementDetailsSerializer
    queryset = Achievement.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return APIResponse.success(
            data=serializer.data, 
            message= res_msg.ACHIEVEMENT_LIST[self.RES_LANG]
        )

class UpdateAchievement(generics.UpdateAPIView):
    """API View to update Experience details with id"""
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateAchievementSerializer
    queryset = Achievement.objects.all()

    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_public_id = instance.icon_image_public_id

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if 'icon_image' in request.FILES and old_public_id:
            try:
                image_manager = CloudinaryImageManager()
                image_manager.delete(old_public_id)
            except Exception as e:
                logger.warning(f"Failed to delete old image: {e}")
        
        achievement = serializer.save()
        achievement_data = AchievementDetailsSerializer(achievement).data

        return APIResponse.success(
            data=achievement_data,
            message= res_msg.ACHIEVEMENT_UPDATED[self.RES_LANG],
            status=status.HTTP_200_OK
        )

class DeleteAchievement(generics.DestroyAPIView):
    """API View to delete achievement with id"""
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    queryset = Achievement.objects.all()
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message= res_msg.ACHIEVEMENT_DELETE[self.RES_LANG],
            status=status.HTTP_200_OK
        )
    
