from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aps_urn = models.CharField("URN do modelo (APS/Tandem)", max_length=512, blank=True, default="")
    tandem_twin_id = models.CharField("Tandem Twin ID (opcional)", max_length=256, blank=True, default="")
    tandem_project_id = models.CharField("Tandem Project ID (opcional)", max_length=256, blank=True, default="")

    def __str__(self):
        return f"Perfil de {self.user.username}"
