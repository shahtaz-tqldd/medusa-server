from django.urls import path, include
from .views import (
    CreateNewService,
    ServiceDetails,
    ServiceList,
    UpdateService,
    DeleteService,
    SkillDetailsView,
    UpdateSkillDetails,
    CreateNewExperience,
    ExperienceList,
    ExperienceDetails,
    UpdateExperienceDetails,
    DeleteExperience,
    AchievementList,
    CreateAchievement,
    UpdateAchievement,
    DeleteAchievement,
)

app_name = "services"

service_urls = [
    path("", ServiceList.as_view(), name="service-list"),
    path("<uuid:id>/", ServiceDetails.as_view(), name="service-details"),
    path("create/", CreateNewService.as_view(), name="create-service"),
    path("update/<uuid:id>/", UpdateService.as_view(), name="update-service"),
    path("delete/<uuid:id>/", DeleteService.as_view(), name="delete-service"),
]

skill_urls = [
    path("", SkillDetailsView.as_view(), name="skill-details"),
    path("update/", UpdateSkillDetails.as_view(), name="update-skill"),
]

experience_urls = [
    path("", ExperienceList.as_view(), name="experience-list"),
    path("<uuid:id>/", ExperienceDetails.as_view(), name="experience-details"),
    path("create/", CreateNewExperience.as_view(), name="create-experience"),
    path("update/<uuid:id>/", UpdateExperienceDetails.as_view(), name="update-experience"),
    path("delete/<uuid:id>/", DeleteExperience.as_view(), name="delete-experience"),
]

achievement_urls = [
    path("", AchievementList.as_view(), name="achievement-list"),
    path("create/", CreateAchievement.as_view(), name="create-achievement"),
    path("update/<uuid:id>/", UpdateAchievement.as_view(), name="update-achievement"),
    path("delete/<uuid:id>/", DeleteAchievement.as_view(), name="delete-achievement"),
]

urlpatterns = [
    path("", include(service_urls)),
    path("skills/", include(skill_urls)),
    path("experiences/", include(experience_urls)),
    path("achievements/", include(achievement_urls)),
]
