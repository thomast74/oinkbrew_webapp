# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-13 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_auto_20160327_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='archived',
            field=models.BooleanField(default=False, verbose_name=b'Archived'),
        ),
    ]
