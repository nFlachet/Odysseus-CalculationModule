from django.db import models


class Kpi(models.Model):
    kpi_name  = models.CharField(primary_key=True, max_length=64)
    kpi_scope_building = models.BooleanField(default=False)
    kpi_scope_room = models.BooleanField(default=False)
    kpi_tenant_Roma = models.BooleanField(default=False)
    kpi_tenant_Manchester = models.BooleanField(default=False)
    kpi_description = models.TextField()
