from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    get_object_or_404)

from noise_sensor_api.models import NoiseData
from noise_sensor_api.serializers import ObservationSerializer


class MultipleFieldLookupMixin(object):
    """
    Filter with multiple lookup fields instead of using the
    lookup_field variable.
    """
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter = {}

        for field in self.lookup_fields:
            if self.kwargs[field]:
                filter[field] = self.kwargs[field]

        obj = get_object_or_404(queryset, **filter)
        if obj:
            self.check_object_permissions(self.request, obj)

        return obj


class ObservationListView(ListAPIView):
    queryset = NoiseData.objects.using('kafka_noise_db').all()
    serializer_class = ObservationSerializer


class ObservationRetrieveView(MultipleFieldLookupMixin, RetrieveAPIView):
    queryset = NoiseData.objects.using('kafka_noise_db').all()
    http_method_names = ['get']
    serializer_class = ObservationSerializer
    lookup_fields = ('connect_topic', 'connect_partition', 'connect_offset',)
