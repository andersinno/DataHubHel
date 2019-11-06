import random
from typing import Type

from django.db import transaction

from .models import TA120Sensor
from .properties import DATA_PROPERTIES


def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))

    return inner


# We need to make sure that datastream (M2MField) gets
# correctly attached to TA120Sensor after it is commited to db.


@on_transaction_commit
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
