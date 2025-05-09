from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.app_run, name="home"),
    path('admin/', admin.site.urls),
    path('auth/', include('user.v1.urls')),
    path('base/', include('base.v1.urls')),
] 

# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
