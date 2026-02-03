from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_followup, name="create_followup"),
    path("edit/<int:pk>/", views.edit_followup, name="edit_followup"),
    path("mark-done/<int:pk>/", views.mark_done, name="mark_done"),

    # Public page
    path("p/<str:token>/", views.public_followup, name="public_followup"),
]
