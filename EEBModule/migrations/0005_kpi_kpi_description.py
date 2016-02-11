# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0004_auto_20151019_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='kpi',
            name='kpi_description',
            field=models.CharField(default='', max_length=256),
        ),
    ]
