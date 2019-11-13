from rest_framework import serializers


class AuthParametersSerializer(serializers.Serializer):
    k = serializers.CharField(
        label="key", help_text="API key")
    i = serializers.CharField(
        label="device_id", help_text="device identifier")


class QueryParametersSerializer(serializers.Serializer):
    t = serializers.DateTimeField(
        label="time", help_text="timestamp", required=False)
    getCmd = serializers.BooleanField(  # noqa: N815
        default=True, initial=True, required=False,
        label="get_command", help_text="request for receive commands")


class SensorDataSerializer(serializers.Serializer):
    n = serializers.FloatField(
        label="level", help_text="sound pressure level")
    o = serializers.NullBooleanField(
        label="overload", help_text="overload", required=False)
    u = serializers.NullBooleanField(
        label="underrange", help_text="underrange", required=False)
    b = serializers.FloatField(
        label="battery", help_text="battery level", required=False)
    p = serializers.NullBooleanField(
        label="power", help_text="power supply status", required=False)
    w = serializers.FloatField(
        label="wifi_strength", help_text="wi-fi strength", required=False)
    m = serializers.FloatField(
        label="modem_strength", help_text="modem strength", required=False)
    s = serializers.CharField(
        label="laeq1s_registers", help_text="LAeq1s registers", required=False)
