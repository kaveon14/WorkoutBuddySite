# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-27 05:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WBBackend', '0014_auto_20180124_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customexercise',
            name='exercise_description',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='defaultexercise',
            name='exercise_description',
            field=models.TextField(max_length=1000),
        ),
    ]