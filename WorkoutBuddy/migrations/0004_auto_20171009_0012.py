# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-09 00:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkoutBuddy', '0003_exercisegoals'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercisegoals',
            name='goal_reps',
            field=models.CharField(max_length=10),
        ),
    ]
