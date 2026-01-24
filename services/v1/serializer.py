import logging
from rest_framework import serializers
from base.managers.cloudinary import CloudinaryImageManager

from services.models import (
    Services,
    ProjectService,  
    SkillsAndIntroduction, 
    Experience,
    Achievement
)
from projects.models import Project

logger = logging.getLogger(__name__)


class CreateServiceSerializer(serializers.ModelSerializer):
    """Serializer to create new service"""
    featured_image = serializers.ImageField(required=False, allow_null=True)
    projects = serializers.JSONField(required=False, write_only=True)
    features = serializers.JSONField(required=False)
    tech_stacks = serializers.JSONField(required=False)
    
    class Meta:
        model = Services
        fields = ['name', 'description', 'featured_image', 'features', 'tech_stacks', 'projects']
        extra_kwargs = {
            'order': {'required': False},
        }

    def create(self, validated_data):
        # Extract projects and featured_image from validated data
        projects_ids = validated_data.pop('projects', [])
        featured_image = validated_data.pop('featured_image', None)
        
        # Ensure features and tech_stacks are lists (they come as parsed JSON already)
        features = validated_data.get('features', [])
        tech_stacks = validated_data.get('tech_stacks', [])
        
        # Validate that they are lists
        if not isinstance(features, list):
            validated_data['features'] = []
        if not isinstance(tech_stacks, list):
            validated_data['tech_stacks'] = []
        if not isinstance(projects_ids, list):
            projects_ids = []
        
        # Handle image upload if provided
        if featured_image:
            try:
                image_manager = CloudinaryImageManager()
                upload_result = image_manager.upload(
                    image_file=featured_image,
                    folder="services"
                )
                validated_data['featured_image'] = upload_result['url']
                validated_data['featured_image_public_id'] = upload_result['public_id']
            except Exception as e:
                raise serializers.ValidationError({
                    'featured_image': f'Image upload failed: {str(e)}'
                })
        
        # Create the service
        service = Services.objects.create(**validated_data)
        
        # Create ProjectService relationships
        if projects_ids:
            for project_id in projects_ids:
                try:
                    project = Project.objects.get(id=project_id)
                    ProjectService.objects.create(
                        project=project,
                        service=service,
                        role="Full-Stack Development"  # Default role
                    )
                except Project.DoesNotExist:
                    # Log warning but continue processing
                    logger.warning(f"Project with id {project_id} not found")
                    continue
        
        return service
    
    def update(self, instance, validated_data):
        # Extract projects and featured_image from validated data
        projects_ids = validated_data.pop('projects', None)
        featured_image = validated_data.pop('featured_image', None)
        
        # Ensure features and tech_stacks are lists if provided
        if 'features' in validated_data:
            features = validated_data.get('features', [])
            if not isinstance(features, list):
                validated_data['features'] = []
        
        if 'tech_stacks' in validated_data:
            tech_stacks = validated_data.get('tech_stacks', [])
            if not isinstance(tech_stacks, list):
                validated_data['tech_stacks'] = []
        
        # Handle image upload if provided
        if featured_image:
            try:
                image_manager = CloudinaryImageManager()
                upload_result = image_manager.upload(
                    image_file=featured_image,
                    folder="services"
                )
                validated_data['featured_image'] = upload_result['url']
                validated_data['featured_image_public_id'] = upload_result['public_id']
            except Exception as e:
                raise serializers.ValidationError({
                    'featured_image': f'Image upload failed: {str(e)}'
                })
        
        # Update the service instance with validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ProjectService relationships if projects are provided
        if projects_ids is not None:
            if not isinstance(projects_ids, list):
                projects_ids = []
            
            # Delete existing relationships
            ProjectService.objects.filter(service=instance).delete()
            
            # Create new relationships
            for project_id in projects_ids:
                try:
                    project = Project.objects.get(id=project_id)
                    ProjectService.objects.create(
                        project=project,
                        service=instance,
                        role="Full-Stack Development"  # Default role
                    )
                except Project.DoesNotExist:
                    # Log warning but continue processing
                    logger.warning(f"Project with id {project_id} not found")
                    continue
        
        return instance


class ServiceDetailsSerializer(serializers.ModelSerializer):
    """Serializer to show service details"""
    projects = serializers.SerializerMethodField()
    
    class Meta:
        model = Services
        fields = '__all__'
    
    def get_projects(self, obj):
        """Get all projects associated with this service"""
        project_services = ProjectService.objects.filter(service=obj).select_related('project')
        return [
            {
                'id': ps.project.id,
                'title': ps.project.title,
                'role': ps.role
            }
            for ps in project_services
        ]


# -----------------------------
# SKILLS AND INTRODUCTION
# -----------------------------
class SkillsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsAndIntroduction
        fields = "__all__"


# -----------------------------
# EXPERIENCE
# -----------------------------
class CreateExperienceSerializer(serializers.ModelSerializer):
    """Serializer to create new work experience"""
    class Meta:
        model = Experience
        fields = '__all__'


class ExperienceDetailsSerializer(serializers.ModelSerializer):
    """Serializer to show experiences"""
    class Meta:
        model = Experience
        fields = '__all__'


# -----------------------------
# ACHIEVEMENT
# -----------------------------
class CreateAchievementSerializer(serializers.ModelSerializer):
    icon_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Achievement
        fields = [
            'title',
            'subtitle',
            'icon_image',
            'score',
            'type',
            'credential_url',
        ]

    def create(self, validated_data):
        icon_image = validated_data.pop('icon_image', None)

        if icon_image:
            image_manager = CloudinaryImageManager()
            upload_result = image_manager.upload(
                image_file=icon_image,
                folder="achievements"
            )
            validated_data['icon_image'] = upload_result['url']
            validated_data['icon_image_public_id'] = upload_result['public_id']

        return Achievement.objects.create(**validated_data)

    def update(self, instance, validated_data):
        icon_image = validated_data.pop('icon_image', None)

        if icon_image:
            image_manager = CloudinaryImageManager()

            # delete old image if exists
            if instance.icon_image_public_id:
                try:
                    image_manager.delete(instance.icon_image_public_id)
                except Exception:
                    pass

            upload_result = image_manager.upload(
                image_file=icon_image,
                folder="achievements"
            )

            instance.icon_image = upload_result['url']
            instance.icon_image_public_id = upload_result['public_id']

        # update other fields normally
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



class AchievementDetailsSerializer(serializers.ModelSerializer):
    """Serializer to show achievements"""
    class Meta:
        model = Achievement
        fields = '__all__'
