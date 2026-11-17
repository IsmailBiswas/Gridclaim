from django.urls import path

from apps.board import views

app_name = "board"

urlpatterns = [
    path("", views.home, name="home"),
    path("cells/<int:cell_id>/claim/", views.claim_cell, name="claim"),
    path("cells/<int:cell_id>/", views.cell_partial, name="cell"),
    path("sidebar/", views.sidebar_partial, name="sidebar"),
]