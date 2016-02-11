# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0002_auto_20151019_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='kpis',
            name='kpi_scope',
            field=models.IntegerField(default=0),
        ),
    ]
