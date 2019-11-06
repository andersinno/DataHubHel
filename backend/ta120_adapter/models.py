from typing import Mapping

from django.db import models

from datahubhel.base_models import TimestampedUUIDModel
from datahubhel.core.models import Datastream, Sensor, Thing


class TA120Sensor(TimestampedUUIDModel):
    id_sensor = models.CharField(max_length=60, unique=True)
    key = models.CharField(max_length=128)
    datastreams = models.ManyToManyField(
        Datastream,
        blank=True)
    sensor = models.ForeignKey(
        Sensor,
        related_name='+',
        on_delete=models.PROTECT)
    thing = models.ForeignKey(
        Thing,
        related_name='+',
        on_delete=models.PROTECT)

    def get_datastream_map(self) -> Mapping[str, int]:
        return dict(self.datastreams.values_list('name', 'pk'))
