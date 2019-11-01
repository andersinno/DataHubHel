import json
from typing import Any, Callable, Mapping, Tuple

from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from datahubhel.gateway_utils import (
    generate_ids,
    get_kafka_producer,
    make_ms_timestamp,
)

from .authentication import SensorKeyAuthentication
from .models import Sensor
from .properties import DATA_PROPERTIES
from .serializers import QueryParametersSerializer, SensorDataSerializer
from .ul20 import UltraLight20Parser, UltraLight20Renderer
from .utils import dump_laeq1s_registers

TOPIC = 'fi.fvh.observations.noise.ta120'

SERIALIZERS = {
    'laeq1s_registers': dump_laeq1s_registers,
}

# Map each property key to a pair of label and serializer,
# e.g. "n" is mapped to ("level", json.dumps).
PROPERTIES: Mapping[str, Tuple[str, Callable[[Any], str]]] = {
    key: (prop.label, SERIALIZERS.get(prop.label, json.dumps))
    for (key, prop) in DATA_PROPERTIES.items()
}


class Endpoint(generics.GenericAPIView):
    parser_classes = [
        UltraLight20Parser,
        FormParser,
        MultiPartParser,
    ]
    renderer_classes = [
        UltraLight20Renderer,
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    authentication_classes = [SensorKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SensorDataSerializer

    def post(self, request, format=None):
        params_parser = QueryParametersSerializer(data=request.query_params)
        params_parser.is_valid(raise_exception=True)
        params = params_parser.validated_data

        body_parser = self.get_serializer(data=request.data)
        body_parser.is_valid(raise_exception=True)
        data = body_parser.validated_data

        # assert isinstance(request.user, SensorUser)
        sensor = request.user.sensor  # type: Sensor
        datastreams = sensor.get_datastream_map()

        event_time = make_ms_timestamp(params.get('t'))

        producer = get_kafka_producer()
        ids = iter(generate_ids())
        for (prop_key, prop_value) in data.items():
            (name, serializer) = PROPERTIES[prop_key]
            producer.produce(topic=TOPIC, key=sensor.identifier, value={
                'id': next(ids),
                'time': event_time,
                'datastream': datastreams[prop_key],
                'value': serializer(prop_value),
            })
        producer.flush()

        return Response()

        # Parameters of the sensor can be changed in the response,
        # e.g. something like this (to set averaging time to 30 secs):
        # return Response({
        #     '{.sensor_id}@setConfig'.format(sensor): 't=0030',
        # })
