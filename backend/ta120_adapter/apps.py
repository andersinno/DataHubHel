from django.apps import AppConfig
from django.db.models.signals import post_save


class TA120AdapterConfig(AppConfig):
    name = 'ta120_adapter'

    def ready(self):
        from .signal_handlers import add_ta120sensor_datastreams
        from .models import TA120Sensor
        post_save.connect(add_ta120sensor_datastreams, sender=TA120Sensor)
