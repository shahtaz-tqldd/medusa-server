from django.urls import path, include
from .views import (
    CreateNewBlog,
    BlogList,
    BlogDetails,
    UpdateBlogDetails,
    DeleteBlog,
    CategoryList,
    CreateNewCategory,
    UpdateCategory,
    DeleteCategory,
    TagList,
    CreateNewTag,
    UpdateTag,
    DeleteTag,
)

app_name = 'blogs'

category_urls = [
    path("list/", CategoryList.as_view(), name="category-list"),
    path("create/", CreateNewCategory.as_view(), name="create-category"),
    path("update/<id>/", UpdateCategory.as_view(), name="update-category"),
    path("delete/<id>/", DeleteCategory.as_view(), name="delete-category"),
]

tags_urls = [
    path("list/", TagList.as_view(), name="tag-list"),
    path("create/", CreateNewTag.as_view(), name="create-tag"),
    path("update/<id>/", UpdateTag.as_view(), name="update-tag"),
    path("delete/<id>/", DeleteTag.as_view(), name="delete-tag"),
]

blog_urls = [
    path("list/", BlogList.as_view(), name="blog-list"),
    path("create/", CreateNewBlog.as_view(), name="create-blog"),
    path("<id>/", BlogDetails.as_view(), name="blog-details"),
    path("update/<id>/", UpdateBlogDetails.as_view(), name="update-blog"),
    path("delete/<id>/", DeleteBlog.as_view(), name="delete-blog"),
]

urlpatterns = blog_urls + [
  path('categories/', include(category_urls)), 
  path('tags/', include(tags_urls))
] 
