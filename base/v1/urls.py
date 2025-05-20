from django.urls import path, include
from .views import CreateVisitor, VisitorList

visitor_urls = [
    path("list/", VisitorList.as_view(), name="visitor-list"),
    path("create/", CreateVisitor.as_view(), name="create-visitor"),
]

urlpatterns = [path('visitors/', include(visitor_urls))]