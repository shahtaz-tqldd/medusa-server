from django.urls import path
from .views import (
    CreateNewProject,
    ProjectList,
    ProjectDetails,
    UpdateProjectDetails,
    DeleteProject
)

app_name = 'projects'

urlpatterns = [
    path("create/", CreateNewProject.as_view(), name="create-project"),
    path("list/", ProjectList.as_view(), name="project-list"),
    path("<project_id>/", ProjectDetails.as_view(), name="project-details"),
    path("update/<project_id>/", UpdateProjectDetails.as_view(), name="update-project"),
    path("delete/<project_id>/", DeleteProject.as_view(), name="delete-project"),
]
