from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "aps_urn", "tandem_project_id", "tandem_twin_id")
    search_fields = ("user__username", "aps_urn", "tandem_project_id", "tandem_twin_id")
