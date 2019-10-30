import hmac

from django.utils.translation import ugettext as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import TA120Sensor
from .serializers import AuthParametersSerializer


class SensorUser:
    is_authenticated = True
    is_staff = False
    is_superuser = False

    def __init__(self, sensor):
        self.sensor = sensor

    def __str__(self):
        return str(self.sensor)


class SensorKeyAuthentication(BaseAuthentication):
    queryset = TA120Sensor.objects.all()

    def authenticate(self, request):
        (sensor_id, key) = self.get_credentials(request)
        return self.authenticate_credentials(sensor_id, key)

    def get_credentials(self, request):
        parser = AuthParametersSerializer(data=request.query_params)
        if not parser.is_valid():
            raise AuthenticationFailed(_('Unable to extract credentials'))

        sensor_id = parser.validated_data['i']
        key = parser.validated_data['k']
        return (sensor_id, key)

    def authenticate_credentials(self, sensor_id, key):
        sensor = self.queryset.filter(sensor_id=sensor_id).first()
        correct_key = sensor.key if sensor else ''
        if hmac.compare_digest(correct_key, key) and correct_key:
            return (SensorUser(sensor), sensor)
        raise AuthenticationFailed(_('Sensor authentication failed'))
