# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(default=b'PENDING', max_length=10)),
                ('task', models.CharField(max_length=256, db_index=True)),
                ('task_id', models.CharField(unique=True, max_length=36, db_index=True)),
                ('category', models.CharField(max_length=50)),
                ('args', models.TextField(blank=True)),
                ('kwargs', models.TextField(blank=True)),
                ('result', models.TextField(blank=True)),
                ('scheduled', models.BooleanField(default=False)),
                ('timestamp_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('timestamp_modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('timestamp_prerun', models.DateTimeField(null=True, editable=False, blank=True)),
                ('timestamp_postrun', models.DateTimeField(null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
