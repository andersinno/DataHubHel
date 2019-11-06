# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models

from datahubhel.core.models import Datastream


class Observation(models.Model):
    datastream = models.ForeignKey(
        Datastream,
        db_column='DATASTREAM',
        blank=True,
        null=True,
        on_delete=models.PROTECT)
    time = models.BigIntegerField(
        db_column='TIME',
        blank=True,
        null=True)
    id = models.TextField(
        db_column='ID',
        primary_key=True)
    value = models.TextField(
        db_column='VALUE',
        blank=True,
        null=True)

    class Meta:
        managed = False
        db_table = 'OBSERVATION'
