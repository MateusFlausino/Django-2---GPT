from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # ⬅️ use a view nativa
# ❌ apague esta linha que causa erro:
# from core.views import LoginViewCustom, logout_view

urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin.site.urls),

    # Auth (views nativas)
    path("accounts/login/",
         auth_views.LoginView.as_view(
             template_name="registration/login.html",
             redirect_authenticated_user=True
         ),
         name="login"),
    path("accounts/logout/",
         auth_views.LogoutView.as_view(next_page="login"),
         name="logout"),
]
