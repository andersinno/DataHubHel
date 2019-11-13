from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from datahubhel.base_models import EntityBase, TimestampedUUIDModel


class Location(models.Model):
    name = models.CharField(verbose_name=_("address"), max_length=100)
    description = models.TextField(blank=True)
    coordinates = PointField(
        verbose_name=_("coordinates"),
        null=True,
        blank=True)

    def __str__(self):
        return self.name


class Thing(EntityBase):
    location = models.ForeignKey(
        Location,
        verbose_name=_("location"),
        related_name="things",
        on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'thing'
        verbose_name_plural = 'things'
        permissions = (
            ('view_thing_location', 'Can view thing location'),
            ('view_thing_location_history', 'Can view thing location history')
        )


class Sensor(TimestampedUUIDModel):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Datastream(EntityBase):
    thing = models.ForeignKey(
        Thing,
        related_name='datastreams',
        on_delete=models.CASCADE)
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="datastreams")

    class Meta:
        verbose_name = 'data stream'
        verbose_name_plural = 'data streams'
        permissions = (
            ('view_datastream', 'Can view datastream'),
            ('create_observation', 'Can create observation to datastream'),
        )
