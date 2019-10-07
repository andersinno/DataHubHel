from rest_framework import serializers

from noise_sensor_api.models import NoiseData


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoiseData
        fields = '__all__'

    # ('connect_topic', 'connect_partition', 'connect_offset')
