from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.app_run, name="home"),
    path('admin/', admin.site.urls),
    path('base/', include('base.v1.urls')),
    path('auth/', include('user.v1.urls')),
    path('services/', include('services.v1.urls')),
    path('projects/', include('projects.v1.urls')),
    path('blogs/', include('blogs.v1.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
