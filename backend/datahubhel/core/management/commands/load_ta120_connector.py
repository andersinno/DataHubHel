from django.core.management.base import BaseCommand

from datahubhel.ksql_scripts import load_kafka_connectors


class Command(BaseCommand):
    help = 'Load connector for TA120Sensor'

    def handle(self, *args, **options):
        load_kafka_connectors()
