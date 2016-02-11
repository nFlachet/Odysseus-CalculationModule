# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0007_auto_20151019_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kpi',
            name='id',
        ),
        migrations.AlterField(
            model_name='kpi',
            name='kpi_name',
            field=models.CharField(max_length=64, serialize=False, primary_key=True),
        ),
    ]
