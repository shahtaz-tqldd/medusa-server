from django.urls import path, include
from .views import (
  CreateOrUpdateVisitor, 
  VisitorList, 
  ClientList, 
  CreateClient,
  OverviewStats
)

visitor_urls = [
    path("list", VisitorList.as_view(), name="visitor-list"),
    path("init", CreateOrUpdateVisitor.as_view(), name="Create or Update Visitor"),
]

client_urls = [
    path("list/", ClientList.as_view(), name="client-list"),
    path("create/", CreateClient.as_view(), name="create-client"),
]

overview_urls = [
    path("stats/", OverviewStats.as_view(), name="overview-stats"),
]

urlpatterns = [
  path('visitors/', include(visitor_urls)), 
  path('client/', include(client_urls)),
  path('overview/', include(overview_urls)),
]
