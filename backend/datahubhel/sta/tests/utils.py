import datetime

from django.contrib.auth import get_user_model

from datahubhel.core.models import Datastream, Sensor, Thing
from datahubhel.sta.models import Observation


def get_user(username='user-one'):
    return get_user_model().objects.get_or_create(
        username=username, defaults={
            'first_name': 'Firstname',
            'last_name': 'Lastname',
        })[0]


def get_thing(num=1):
    return Thing.objects.get_or_create(
        sts_id=num, defaults={
            'owner': get_user(),
            'name': 'Thing {}'.format(num),
            'description': 'Thing description',
        })[0]


def get_sensor(num=1):
    return Sensor.objects.get_or_create(
        sensor_id=str(num), defaults={
            'thing': get_thing(num=num),
            'name': f'Sensor {num}',
        })[0]


def get_datastream(num=1, thing=None, sensor=None):
    return Datastream.objects.get_or_create(
        sts_id=num, defaults={
            'thing': thing or get_thing(),
            'sensor': sensor or get_sensor(),
            'name': 'Datastream{}'.format(num),
        })[0]


def create_observation(
        name=None,
        id=None,
        datastream_num=None,
        value=None,
):
    if name == 'noise_level':
        id = id or '1234-XYZ-1234'
        datastream_num = datastream_num or 1
        value = 23 if value is None else value
    elif name == 'battery':
        id = '1234-ABC-1234'
        datastream_num = datastream_num or 2
        value = False if value is None else value
    elif not id or not name or not datastream_num:
        raise TypeError

    return Observation.objects.create(
        id=id,
        time=datetime.datetime.now(),
        sensor_id=1,
        property_name=name,
        property_value={"result": value},
        datastream=get_datastream(datastream_num),
    )
