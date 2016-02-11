# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0008_auto_20151019_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='kpi',
            name='kpi_test',
            field=models.BooleanField(default=False),
        ),
    ]
