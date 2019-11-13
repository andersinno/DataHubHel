# Generated by Django 2.0.13 on 2019-10-24 13:25

import uuid

import django.db.models.deletion
from django.conf import settings
from django.contrib.gis.db.models.fields import PointField
from django.db import migrations, models
from django_extensions.db.fields import (
    CreationDateTimeField,
    ModificationDateTimeField,
)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    max_length=100,
                    verbose_name='address')),
                ('description', models.TextField(blank=True)),
                ('coordinates', PointField(
                    blank=True, null=True, srid=4326,
                    verbose_name='coordinates')),
            ],
        ),
        migrations.CreateModel(
            name='Datastream',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('sts_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('owner', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'data stream',
                'verbose_name_plural': 'data streams',
                'permissions': (
                    ('view_datastream', 'Can view datastream'),
                    ('create_observation',
                     'Can create observation to datastream')),
            },
        ),
        migrations.CreateModel(
            name='Thing',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('sts_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('owner', models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(
                     to='datahubhel.Location',
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='things',
                     verbose_name='location')),
            ],
            options={
                'verbose_name': 'thing',
                'verbose_name_plural': 'things',
                'permissions': (
                    ('view_thing_location', 'Can view thing location'),
                    ('view_thing_location_history',
                     'Can view thing location history')),
            },
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('created', CreationDateTimeField(
                    auto_now_add=True, verbose_name='created')),
                ('modified', ModificationDateTimeField(
                    auto_now=True, verbose_name='modified')),
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False)),
                ('name', models.CharField(max_length=60)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='datastream',
            name='thing',
            field=models.ForeignKey(
                to='datahubhel.Thing',
                related_name='datastreams',
                on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='datastream',
            name='sensor',
            field=models.ForeignKey(
                to='datahubhel.Sensor',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='datastreams'),
        ),
    ]
