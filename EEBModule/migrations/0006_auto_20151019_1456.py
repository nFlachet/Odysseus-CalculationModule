# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0005_kpi_kpi_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kpi',
            name='kpi_description',
            field=models.TextField(),
        ),
    ]
