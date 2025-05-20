from django.urls import path, include
from .views import (
    CreateNewService,
    ServiceList,
    UpdateServiceDetails,
    DeleteService,
    CreateNewSkills,
    SkillList,
    UpdateSkillDetails,
    DeleteSkill
)

app_name = 'services'

service_urls = [
    path("", ServiceList.as_view(), name="service-list"),
    path("create/", CreateNewService.as_view(), name="create-service"),
    path("update/<id>/", UpdateServiceDetails.as_view(), name="update-service"),
    path("delete/<id>/", DeleteService.as_view(), name="delete-service"),
]

skill_urls = [
    path("", SkillList.as_view(), name="skill-list"),
    path("create/", CreateNewSkills.as_view(), name="create-Skill"),
    path("update/<id>/", UpdateSkillDetails.as_view(), name="update-skill"),
    path("delete/<id>/", DeleteSkill.as_view(), name="delete-skill"),
]

urlpatterns = service_urls + [path('skills/', include(skill_urls))]
