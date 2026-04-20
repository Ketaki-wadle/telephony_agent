from django.contrib import admin
from django.urls import include, path

from properties.views import favicon_view, home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("favicon.ico", favicon_view, name="favicon"),
    path("admin/", admin.site.urls),
    path("api/", include("properties.urls")),
]
