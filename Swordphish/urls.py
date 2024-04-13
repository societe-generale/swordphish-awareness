from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('LocalUsers.urls')),
    path('', include('Main.urls')),
    path("select2/", include("django_select2.urls")),
]
