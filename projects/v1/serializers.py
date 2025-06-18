from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from projects.models import Project, ProjectImage

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'created_at']


class CreateProjectSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'features',
            'started_at',
            'ended_at',
            'type',
            'live_url',
            'github_url',
            'images'
        ]

        extra_kwargs = {
            'live_url': {'required': False, 'allow_blank': True},
            'github_url': {'required': False, 'allow_blank': True},
            'features': {'required': False},
        }

    def validate(self, attrs):
        # Validate end_date is not before start_date
        start_date = attrs.get('started_at')
        end_date = attrs.get('ended_at')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': _('End date cannot be before start date')
            })
        return attrs

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        project = Project.objects.create(**validated_data)
        
        # Handle image uploads
        for image in images:
            ProjectImage.objects.create(project=project, image=image)
        
        return project
    


class ProjectDetailsSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'features',
            'tech_stacks',
            'started_at',
            'ended_at',
            'type',
            'live_url',
            'github_url',
            'created_at',
            'images'
        ]
