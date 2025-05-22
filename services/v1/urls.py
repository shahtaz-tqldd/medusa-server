from django.urls import path, include
from .views import (
    CreateNewService,
    ServiceList,
    UpdateServiceDetails,
    DeleteService,
    CreateNewSkills,
    SkillList,
    UpdateSkillDetails,
    DeleteSkill,
    CreateNewExperience,
    ExperienceList,
    UpdateExperienceDetails,
    DeleteExperience,
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
    path("create/", CreateNewSkills.as_view(), name="create-skill"),
    path("update/<id>/", UpdateSkillDetails.as_view(), name="update-skill"),
    path("delete/<id>/", DeleteSkill.as_view(), name="delete-skill"),
]

experiences_urls = [
    path("", ExperienceList.as_view(), name="experience-list"),
    path("create/", CreateNewExperience.as_view(), name="create-experience"),
    path("update/<id>/", UpdateExperienceDetails.as_view(), name="update-experience"),
    path("delete/<id>/", DeleteExperience.as_view(), name="delete-experience"),
]

urlpatterns = service_urls + [
    path('skills/', include(skill_urls)),
    path('experience/', include(experiences_urls))
]
