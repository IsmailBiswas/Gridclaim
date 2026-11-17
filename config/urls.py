from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.board.urls")),
    path("me/", include("apps.identity.urls")),
]