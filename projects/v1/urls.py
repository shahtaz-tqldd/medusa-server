from django.urls import path
from .views import (
    CreateNewProject,
    ProjectList,
    ProjectDetails,
    UpdateProject,
    DeleteProject
)

app_name = 'projects'

urlpatterns = [
    path("create", CreateNewProject.as_view(), name="create-project"),
    path("list", ProjectList.as_view(), name="project-list"),
    path("<id>/", ProjectDetails.as_view(), name="project-details"),
    path("update/<id>", UpdateProject.as_view(), name="update-project"),
    path("delete/<id>", DeleteProject.as_view(), name="delete-project"),
]
