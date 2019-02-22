# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-15 03:10
from __future__ import unicode_literals

import TvnfService.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tvnf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tvnfId', models.CharField(default=TvnfService.models.generate_Id, max_length=20, unique=True)),
                ('tvnfStatus', models.CharField(choices=[(b'A', b'Available'), (b'U', b'Unavailable'), (b'F', b'Failed')], default=b'A', max_length=15)),
            ],
            options={
                'ordering': ('tvnfStatus',),
            },
        ),
    ]