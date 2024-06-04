from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("votingapp/", include("votingapp.urls")),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path("admin/", admin.site.urls),
]