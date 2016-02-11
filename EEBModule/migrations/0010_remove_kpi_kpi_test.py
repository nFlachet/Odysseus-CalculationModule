# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0009_kpi_kpi_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kpi',
            name='kpi_test',
        ),
    ]
