from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import LoginViewCustom, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),

    # Auth
    path("accounts/login/", LoginViewCustom.as_view(), name="login"),
    path("accounts/logout/", logout_view, name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
