from rest_framework import serializers
from services.models import Services, Skills


class CreateServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = [
            'name',
            'description',
        ]

        extra_kwargs = {
            'order': {'required': False},
            'started_at': {'required': False},
        }    


class ServiceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'


class CreateSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = [
            'name',
            'description',
            'proficiency_level'
        ]

        extra_kwargs = {
            'order': {'required': False},
            'started_at': {'required': False},
        }


class SkillDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = '__all__'
