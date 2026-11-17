from django.urls import path

from apps.identity import views

app_name = "identity"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
]