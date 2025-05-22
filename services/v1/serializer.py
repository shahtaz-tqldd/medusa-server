from rest_framework import serializers
from services.models import Services, Skills, Experience


class CreateServiceSerializer(serializers.ModelSerializer):
    """Serializer to create new service"""
    class Meta:
        model = Services
        fields = ['name', 'description']
        extra_kwargs = {
            'order': {'required': False},
            'started_at': {'required': False},
        }    


class ServiceDetailsSerializer(serializers.ModelSerializer):
    """Serializer to show service details"""
    class Meta:
        model = Services
        fields = '__all__'


class CreateSkillSerializer(serializers.ModelSerializer):
    """Serializer to create new skill-set"""
    class Meta:
        model = Skills
        fields = ['name', 'description', 'proficiency_level']
        extra_kwargs = {
            'order': {'required': False},
            'started_at': {'required': False},
        }


class SkillDetailsSerializer(serializers.ModelSerializer):
    """Serializer to show skills"""
    class Meta:
        model = Skills
        fields = '__all__'


class CreateExperienceSerializer(serializers.ModelSerializer):
    """Serializer to create new work experience"""
    class Meta:
        model = Experience
        fields = [
            'position', 'details', 'started_at', 'ended_at', 
            'company_name', 'company_location', 'company_logo'
        ]
        extra_kwargs = {
            'order': {'required': False},
            'ended_at': {'required': False},
            'company_logo': {'required': False},
        }


class ExperienceDetailsSerializer(serializers.ModelSerializer):
    """Serializer to show experiences"""
    class Meta:
        model = Experience
        fields = '__all__'
