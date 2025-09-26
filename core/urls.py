from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("assets/", views.asset_list_partial, name="asset_list_partial"),  # HTMX partial
    path("upload/", views.upload_file, name="upload"),
]
