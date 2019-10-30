from typing import Mapping

from django.db import models

from datahubhel.base_models import EntityBase, TimestampedUUIDModel


class Thing(EntityBase):
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

    def get_datastream_map(self) -> Mapping[str, int]:
        return dict(self.datastreams.values_list('name', 'pk'))


class Datastream(EntityBase):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    sensor = models.ForeignKey(
        Sensor, on_delete=models.CASCADE,
        related_name="datastreams")

    class Meta:
        verbose_name = 'data stream'
        verbose_name_plural = 'data streams'
        permissions = (
            ('view_datastream', 'Can view datastream'),
            ('create_observation', 'Can create observation to datastream'),
        )
