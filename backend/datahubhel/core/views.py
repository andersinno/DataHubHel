from rest_framework.generics import ListAPIView

from .models import Thing
from .serializers import SensorSerializer


class Sensor(object):
    """
    This class is just used to represent the
    actual sensor instances. Since we have to combine
    the properties of Sensor and actual sensors for the
    frontend, this class provides properties from both
    of these classes which when serialized gives the output
    exptected by the frontend.
    """
    def __init__(self, identifier, key, name, description=None):
        self.description = description
        self.identifier = identifier
        self.key = key
        self.name = name


class SensorListView(ListAPIView):
    serializer_class = SensorSerializer

    def get_queryset(self):
        user = self.request.user
        things_owned_by_user = Thing.objects.filter(owner=user)
        physical_sensors_related_to_things = [
            sensor
            for thing in things_owned_by_user
            for sensor in thing.physical_sensors.all().select_related('sensor')
        ]
        sensors = [
            Sensor(s.identifier, s.key, s.sensor.name, s.sensor.description)
            for s in physical_sensors_related_to_things
        ]
        return sensors
