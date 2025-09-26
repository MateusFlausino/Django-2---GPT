from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("assets/", views.asset_list_partial, name="asset_list_partial"),  # HTMX partial
    path("upload/", views.upload_file, name="upload"),

    # viewer & perfil
    path("viewer/", views.viewer, name="viewer"),
    path("perfil/", views.profile_settings, name="profile"),

    # token para o viewer (APS)
    path("api/aps/token/", views.aps_token, name="aps_token"),
]
