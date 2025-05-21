from django.urls import path, include
from .views import (
  CreateVisitor, 
  VisitorList, 
  ClientList, 
  CreateClient,
)

visitor_urls = [
    path("list/", VisitorList.as_view(), name="visitor-list"),
    path("create/", CreateVisitor.as_view(), name="create-visitor"),
]

client_urls = [
    path("list/", ClientList.as_view(), name="client-list"),
    path("create/", CreateClient.as_view(), name="create-client"),
]

urlpatterns = [
  path('visitors/', include(visitor_urls)), 
  path('client/', include(client_urls))
]
