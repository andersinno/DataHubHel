from rest_framework import serializers

from .models import Datastream


class DatastreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Datastream
        fields = (
            'name',
            'sts_id',
            'description',
        )
        read_only_fields = fields


class SensorSerializer(serializers.Serializer):
    description = serializers.CharField(
        style={'base_template': 'textarea.html'}
    )
    identifier = serializers.CharField(max_length=60)
    key = serializers.CharField(max_length=128)
    name = serializers.CharField(max_length=60)

    class Meta:
        fields = '__all__'
