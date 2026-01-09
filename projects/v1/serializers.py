import json
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from projects.models import Project, ProjectImage, ProjectLink
from base.managers.cloudinary import CloudinaryImageManager


class ProjectLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectLink
        fields = ['id', 'type', 'label', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ['id', 'image_url', 'public_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateProjectSerializer(serializers.ModelSerializer):
    # File fields for upload
    featured_image = serializers.ImageField(write_only=True, required=False)
    project_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    # JSON string fields from FormData
    tech_stacks = serializers.CharField(required=False, allow_blank=True)
    features = serializers.CharField(required=False, allow_blank=True)
    links = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'case_study',
            'type',
            'tech_stacks',
            'features',
            'links',
            'featured_image',
            'project_images',
        ]

        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True},
            'case_study': {'required': False, 'allow_blank': True},
            'type': {'required': False},
        }

    def validate_tech_stacks(self, value):
        """Parse JSON string to list"""
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Tech stacks must be a list")
            return parsed
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for tech stacks")

    def validate_features(self, value):
        """Parse JSON string to list"""
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Features must be a list")
            return parsed
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for features")

    def validate_links(self, value):
        """Parse JSON string to list of link objects"""
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Links must be a list")
            
            # Validate each link has required fields
            for link in parsed:
                if not all(key in link for key in ['type', 'label', 'url']):
                    raise serializers.ValidationError(
                        "Each link must have 'type', 'label', and 'url'"
                    )
            return parsed
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for links")

    def create(self, validated_data):
        # Extract file and array data
        featured_image = validated_data.pop('featured_image', None)
        project_images = validated_data.pop('project_images', [])
        tech_stacks = validated_data.pop('tech_stacks', [])
        features = validated_data.pop('features', [])
        links_data = validated_data.pop('links', [])

        # Initialize Cloudinary manager
        cloudinary_manager = CloudinaryImageManager()

        # Upload featured image to Cloudinary
        if featured_image:
            try:
                featured_result = cloudinary_manager.upload(
                    featured_image, 
                    folder="projects/featured"
                )
                validated_data['featured_image_url'] = featured_result['url']
                validated_data['featured_image_public_id'] = featured_result['public_id']
            except Exception as e:
                raise serializers.ValidationError({
                    'featured_image': f'Failed to upload featured image: {str(e)}'
                })

        # Set array fields
        validated_data['tech_stacks'] = tech_stacks
        validated_data['features'] = features

        # Create project
        project = Project.objects.create(**validated_data)

        # Upload project images to Cloudinary
        if project_images:
            try:
                image_results = cloudinary_manager.bulk_upload(
                    project_images, 
                    folder="projects/screens"
                )
                
                # Create ProjectImage records
                for result in image_results:
                    ProjectImage.objects.create(
                        project=project,
                        image_url=result['url'],
                        public_id=result['public_id'],
                    )
            except Exception as e:
                # If image upload fails, we might want to delete the project
                # or just log the error and continue
                raise serializers.ValidationError({
                    'project_images': f'Failed to upload project images: {str(e)}'
                })

        # Create project links
        for link_data in links_data:
            ProjectLink.objects.create(
                project=project,
                type=link_data['type'],
                label=link_data['label'],
                url=link_data['url']
            )

        return project


class ProjectDetailsSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)
    links = ProjectLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'case_study',
            'featured_image_url',
            'type',
            'tech_stacks',
            'features',
            'links',
            'images',
            'created_at',
            'updated_at',
        ]


class UpdateProjectSerializer(serializers.ModelSerializer):
    # File fields for upload
    featured_image = serializers.ImageField(write_only=True, required=False)
    project_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    # JSON string fields from FormData
    tech_stacks = serializers.CharField(required=False, allow_blank=True)
    features = serializers.CharField(required=False, allow_blank=True)
    links = serializers.CharField(required=False, allow_blank=True)
    
    # IDs of images to delete
    delete_image_ids = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'case_study',
            'type',
            'tech_stacks',
            'features',
            'links',
            'featured_image',
            'project_images',
            'delete_image_ids',
        ]

        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False, 'allow_blank': True},
            'case_study': {'required': False, 'allow_blank': True},
            'type': {'required': False},
        }

    def validate_tech_stacks(self, value):
        if not value:
            return None
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Tech stacks must be a list")
            return parsed
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for tech stacks")

    def validate_features(self, value):
        if not value:
            return None
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Features must be a list")
            return parsed
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for features")

    def validate_links(self, value):
        if not value:
            return None
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Links must be a list")
            
            for link in parsed:
                if not all(key in link for key in ['type', 'label', 'url']):
                    raise serializers.ValidationError(
                        "Each link must have 'type', 'label', and 'url'"
                    )
            return parsed
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for links")

    def validate_delete_image_ids(self, value):
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Delete image IDs must be a list")
            return parsed
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for delete image IDs")

    def update(self, instance, validated_data):
        # Extract special fields
        featured_image = validated_data.pop('featured_image', None)
        project_images = validated_data.pop('project_images', [])
        tech_stacks = validated_data.pop('tech_stacks', None)
        features = validated_data.pop('features', None)
        links_data = validated_data.pop('links', None)
        delete_image_ids = validated_data.pop('delete_image_ids', [])

        cloudinary_manager = CloudinaryImageManager()

        # Delete images if requested
        if delete_image_ids:
            images_to_delete = ProjectImage.objects.filter(
                id__in=delete_image_ids, 
                project=instance
            )
            public_ids = [img.public_id for img in images_to_delete]
            
            if public_ids:
                try:
                    cloudinary_manager.bulk_delete(public_ids)
                except Exception as e:
                    raise serializers.ValidationError({
                        'delete_image_ids': f'Failed to delete images: {str(e)}'
                    })
                
                images_to_delete.delete()

        # Update featured image if provided
        if featured_image:
            # Delete old featured image from Cloudinary
            if instance.featured_image_public_id:
                try:
                    cloudinary_manager.delete(instance.featured_image_public_id)
                except Exception:
                    pass  # Continue even if deletion fails

            # Upload new featured image
            try:
                featured_result = cloudinary_manager.upload(
                    featured_image, 
                    folder="projects/featured"
                )
                validated_data['featured_image_url'] = featured_result['url']
                validated_data['featured_image_public_id'] = featured_result['public_id']
            except Exception as e:
                raise serializers.ValidationError({
                    'featured_image': f'Failed to upload featured image: {str(e)}'
                })

        # Update array fields if provided
        if tech_stacks is not None:
            validated_data['tech_stacks'] = tech_stacks
        if features is not None:
            validated_data['features'] = features

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Upload new project images
        if project_images:
            try:
                image_results = cloudinary_manager.bulk_upload(
                    project_images, 
                    folder="projects/screens"
                )
                
                for result in image_results:
                    ProjectImage.objects.create(
                        project=instance,
                        image_url=result['url'],
                        public_id=result['public_id'],
                    )
            except Exception as e:
                raise serializers.ValidationError({
                    'project_images': f'Failed to upload project images: {str(e)}'
                })

        # Update links if provided
        if links_data is not None:
            # Delete existing links
            instance.links.all().delete()
            
            # Create new links
            for link_data in links_data:
                ProjectLink.objects.create(
                    project=instance,
                    type=link_data['type'],
                    label=link_data['label'],
                    url=link_data['url']
                )

        return instance