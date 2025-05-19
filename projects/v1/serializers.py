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
            'start_date',
            'end_date',
            'type',
            'live_url',
            'github',
            'images'
        ]

        extra_kwargs = {
            'live_url': {'required': False, 'allow_blank': True},
            'github': {'required': False, 'allow_blank': True},
            'features': {'required': False},
        }

    def validate(self, attrs):
        # Validate end_date is not before start_date
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
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
            'start_date',
            'end_date',
            'type',
            'live_url',
            'github',
            'created_at',
            'images'
        ]
