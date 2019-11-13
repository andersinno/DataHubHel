import uuid
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.db import connection

from datahubhel.core.models import Datastream, Location, Sensor, Thing
from datahubhel.gateway_utils import make_ms_timestamp
from datahubhel.sta.models import Observation


def get_user(username="user-one"):
    return get_user_model().objects.get_or_create(
        username=username,
        defaults={"first_name": "Firstname", "last_name": "Lastname"},
    )[0]


def get_location(location="Turku"):
    location, _ = Location.objects.get_or_create(name="Turku")
    return location


def get_thing(num=1, location=None):
    return Thing.objects.get_or_create(
        sts_id=num,
        defaults={
            "owner": get_user(),
            "name": "Thing {}".format(num),
            "description": "Thing description",
            "location": location or get_location(),
        },
    )[0]


def get_sensor(id=None, name=None):
    return Sensor.objects.get_or_create(
        id=id, defaults={"name": name or "SensorOne"}
    )[0]


def get_datastream(num=1, thing=None, sensor=None, owner=None):
    return Datastream.objects.get_or_create(
        sts_id=num,
        defaults={
            "thing": thing or get_thing(),
            "sensor": sensor or get_sensor(uuid.uuid4()),
            "owner": owner,
        },
    )[0]


def create_observation(name=None, id=None, datastream_num=None, value=None):
    INSERT_INTO_OBSERVATION = """
        INSERT INTO observation (id, time, value, datastream)
        VALUES('{id}', {time}, '{value}', {datastream})
    """
    if name == "noise_level":
        id = id or "1234-XYZ-1234"
        datastream_num = datastream_num or 1
        value = 23 if value is None else value
    elif name == "battery":
        id = "1234-ABC-1234"
        datastream_num = datastream_num or 2
        value = False if value is None else value
    elif not id or not name or not datastream_num:
        raise TypeError
    datastream = get_datastream(datastream_num)
    epoch_time = make_ms_timestamp(datetime.now(tz=timezone.utc))
    with connection.cursor() as cursor:
        cursor.execute(
            INSERT_INTO_OBSERVATION.format(
                id=id, time=epoch_time, value=value, datastream=datastream.id
            )
        )
    return Observation.objects.get(id=id)
