from django.contrib.gis.db import models


class NoiseData(models.Model):
    connect_topic = models.TextField(db_column='__connect_topic', primary_key=True)
    battery = models.FloatField(db_column='BATTERY', blank=True, null=True)
    overload = models.NullBooleanField(db_column='OVERLOAD')
    thing_name = models.TextField(db_column='THING_NAME', blank=True, null=True)
    data_stream = models.IntegerField(db_column='DATASTREAM', blank=True, null=True)
    power = models.NullBooleanField(db_column='POWER')
    lon = models.FloatField(db_column='LON', blank=True, null=True)
    time = models.BigIntegerField(db_column='TIME', blank=True, null=True)
    level = models.FloatField(db_column='LEVEL', blank=True, null=True)
    connect_partition = models.IntegerField(db_column='__connect_partition')
    connect_offset = models.BigIntegerField(db_column='__connect_offset')
    sensor_name = models.TextField(db_column='SENSOR_NAME', blank=True, null=True)
    lat = models.FloatField(db_column='LAT', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'LOUDNOISE'
        unique_together = (('connect_topic', 'connect_partition', 'connect_offset'),)


class MinBattery(models.Model):
    connect_topic = models.TextField(db_column='__connect_topic', primary_key=True)
    battery = models.FloatField(db_column='BATTERY', blank=True, null=True)
    connect_partition = models.IntegerField(db_column='__connect_partition')
    connect_offset = models.BigIntegerField(db_column='__connect_offset')
    sensor_name = models.TextField(db_column='SENSOR_NAME', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MIN_BATTERY'
        unique_together = (('connect_topic', 'connect_partition', 'connect_offset'),)
