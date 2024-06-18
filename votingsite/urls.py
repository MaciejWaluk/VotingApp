from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("votingapp.urls")),
    path('docs/', include('docs.urls')),
    path("admin/", admin.site.urls),
]