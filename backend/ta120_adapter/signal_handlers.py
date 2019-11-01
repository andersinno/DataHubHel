import random
from typing import Type

from .models import TA120Sensor
from .properties import DATA_PROPERTIES


def add_ta120sensor_datastreams(
    sender: Type[TA120Sensor], instance: TA120Sensor, **kwargs: object
):
    for (key, prop) in DATA_PROPERTIES.items():
        instance.datastreams.get_or_create(
            name=key,
            defaults={
                "thing": instance.thing,
                "sensor": instance.sensor,
                "sts_id": random.randint(
                    1, 2 ** 31 - 1
                ),  # TODO: Do something about this
                "description": prop.description,
            },
        )
