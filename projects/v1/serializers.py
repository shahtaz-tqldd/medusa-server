from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework import serializers

from projects.models import Project, ProjectImage
from base.helpers.func import extra_kwargs_constructor

class CreateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["name", "description", "type"]

        extra_kwargs = extra_kwargs_constructor(
            "github_url"
        )



class ProjectDetailsSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = "__all__"

