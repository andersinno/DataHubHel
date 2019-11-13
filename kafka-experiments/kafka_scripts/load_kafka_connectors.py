import logging
from typing import List
from urllib.parse import urlparse

import requests

from . import settings
from .http_response_check import check_errors

LOG = logging.getLogger(__name__)

SINK_CONFIGURATIONS = {
    "noise-sink": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "topics": "LOUDNOISE",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": settings.SCHEMA_REGISTRY_URL,
        "connection.url": "jdbc:" + settings.SINK_DATABASE_URL,
        "connection.user": "postgres",
        "connection.password": "postgres",
        "auto.create": "true",
        "auto.evolve": "true",
        "insert.mode": "upsert",
        "pk.mode": "record_key",
        "pk.fields": "SENSOR_NAME"
    },
    "min-sink": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "topics": "MIN_BATTERY",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": settings.SCHEMA_REGISTRY_URL,
        "connection.url": "jdbc:" + settings.SINK_DATABASE_URL,
        "connection.user": "postgres",
        "connection.password": "postgres",
        "auto.create": "true",
        "auto.evolve": "true",
        "insert.mode": "upsert",
        "pk.mode": "record_key",
        "pk.fields": "SENSOR_NAME"
    },
    "es-sink": {
        "connector.class": (
            "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector"),
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": settings.SCHEMA_REGISTRY_URL,
        "connection.url": settings.ELASTICSEARCH_URL,
        "type.name": "_doc",
        "topics": "LOUDNOISE",
        "key.ignore": True,
        "schema.ignore": True,
    },
    "es-location-sink": {
        "connector.class": (
            "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector"),
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": settings.SCHEMA_REGISTRY_URL,
        "connection.url": settings.ELASTICSEARCH_URL,
        "type.name": "_doc",
        "topics": "ELASTIC_LOCATION_STREAM",
        "key.ignore": True,
        "schema.ignore": True
    },
    "enriched-observation-sink": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "topics": settings.LOCATION_ENRICHED_OBS,
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": settings.SCHEMA_REGISTRY_URL,
        "connection.url": "jdbc:" + settings.SINK_DATABASE_URL,
        "connection.user": "postgres",
        "connection.password": "postgres",
        "auto.create": "true",
        "auto.evolve": "true",
        "insert.mode": "upsert",
        "pk.mode": "record_value",
        "pk.fields": "ID"
    },
    "datahubhel-source": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
        "connection.url": "jdbc:" + settings.SOURCE_DATABASE_URL,
        "connection.user": "datahubhel",
        "connection.password": "datahubhel",
        "topic.prefix": "ta120_",
        "mode": "bulk",
        "table.whitelist": "datahubhel_datastream, \
            datahubhel_thing, \
            datahubhel_location",
    }
}


def load_kafka_connectors():
    existing_connectors = _get_existing_connectors()
    for configuration_name in SINK_CONFIGURATIONS:
        if configuration_name in existing_connectors:
            LOG.info("Connector already exists: %s", configuration_name)
            continue
        _load_connector(configuration_name)


def _get_existing_connectors() -> List[str]:
    response = requests.get(f'{settings.KAFKA_CONNECT_URL}/connectors')
    check_errors(response)
    result = response.json()
    assert isinstance(result, list)
    assert all(isinstance(x, str) for x in result)
    return result


def _load_connector(configuration_name):
    headers = {
        'Accept': 'application/json',
    }

    data = {
        "name": configuration_name,
        "config": SINK_CONFIGURATIONS[configuration_name],
    }
    data['config'].update(_get_schema_registry_settings())
    response = requests.post(
        f'{settings.KAFKA_CONNECT_URL}/connectors',
        headers=headers,
        json=data,
    )
    check_errors(response)
    LOG.info("Loaded Kafka connector: %s", configuration_name)


def _get_schema_registry_settings():
    result = {
        'value.converter.schema.registry.url': settings.SCHEMA_REGISTRY_URL,
    }

    parsed = urlparse(settings.SCHEMA_REGISTRY_URL)
    if parsed.username and parsed.password:
        creds = '{}:{}'.format(parsed.username, parsed.password)
        result.update({
            'key.converter.basic.auth.credentials.source': 'USER_INFO',
            'value.converter.basic.auth.credentials.source': 'USER_INFO',
            'key.converter.schema.registry.basic.auth.user.info': creds,
            'value.converter.basic.auth.user.info': creds,
        })

    return result


if __name__ == "__main__":
    load_kafka_connectors()
