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
        (id_sensor, key) = self.get_credentials(request)
        return self.authenticate_credentials(id_sensor, key)

    def get_credentials(self, request):
        parser = AuthParametersSerializer(data=request.query_params)
        if not parser.is_valid():
            raise AuthenticationFailed(_('Unable to extract credentials'))

        id_sensor = parser.validated_data['i']
        key = parser.validated_data['k']
        return (id_sensor, key)

    def authenticate_credentials(self, id_sensor, key):
        sensor = self.queryset.filter(id_sensor=id_sensor).first()
        correct_key = sensor.key if sensor else ''
        if hmac.compare_digest(correct_key, key) and correct_key:
            return (SensorUser(sensor), sensor)
        raise AuthenticationFailed(_('Sensor authentication failed'))
