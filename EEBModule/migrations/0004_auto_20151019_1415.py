# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EEBModule', '0003_kpis_kpi_scope'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kpi',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('kpi_name', models.CharField(max_length=64)),
                ('kpi_scope', models.IntegerField(default=0)),
                ('kpi_tenant', models.IntegerField(default=0)),
            ],
        ),
        migrations.DeleteModel(
            name='Kpis',
        ),
    ]
