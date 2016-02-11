# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0006_auto_20151019_1456'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kpi',
            name='kpi_scope',
        ),
        migrations.RemoveField(
            model_name='kpi',
            name='kpi_tenant',
        ),
        migrations.AddField(
            model_name='kpi',
            name='kpi_scope_building',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='kpi',
            name='kpi_scope_room',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='kpi',
            name='kpi_tenant_Manchester',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='kpi',
            name='kpi_tenant_Roma',
            field=models.BooleanField(default=False),
        ),
    ]
