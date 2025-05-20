from django.urls import path
from .views import (
    CreateNewBlog,
    BlogList,
    BlogDetails,
    UpdateBlogDetails,
    DeleteBlog
)

app_name = 'blogs'

urlpatterns = [
    path("create/", CreateNewBlog.as_view(), name="create-blog"),
    path("list/", BlogList.as_view(), name="blog-list"),
    path("<id>/", BlogDetails.as_view(), name="blog-details"),
    path("update/<id>/", UpdateBlogDetails.as_view(), name="update-blog"),
    path("delete/<id>/", DeleteBlog.as_view(), name="delete-blog"),
]
