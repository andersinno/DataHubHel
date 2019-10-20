import os
import json
import requests

SINK_CONFIGURATION_FILES = [
    './kafka_scripts/postgres_sink.json',
    './kafka_scripts/min_sink.json',
    './kafka_scripts/elastic_sink.json',
    './kafka_scripts/elastic_sink_location.json',
]

CONNECT_SERVER = os.getenv(
    'CONNECT_SERVER', 'http://localhost:8083/connectors'
)

REMOTE_CONNECTOR_SETTINGS_MAPPINGS = {
    "key.converter.basic.auth.credentials.source": os.getenv('KEY_CONVERTER_BASIC_AUTH_CREDENTIALS_SOURCE'),
    "key.converter.schema.registry.basic.auth.user.info": os.getenv('BASIC_AUTH_USER_CREDENTIALS'),
    "value.converter.schema.registry.url": os.getenv('VALUE_CONVERTER_SCHEMA_REGISTRY_URL'),
    "value.converter.basic.auth.credentials.source": os.getenv('VALUE_CONVERTER_BASIC_AUTH_CREDENTIALS_SOURCE'),
    "value.converter.basic.auth.user.info": os.getenv('BASIC_AUTH_USER_CREDENTIALS')
}



def _load_connector(file_to_load=""):
    assert file_to_load
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    with open(file_to_load) as f:
        data = json.load(f)
        if os.getenv('build_target') == 'production':
            data.update(REMOTE_CONNECTOR_SETTINGS_MAPPINGS)
    response = requests.post(
        CONNECT_SERVER,
        headers=headers,
        data=json.dumps(data)
    )
    assert response.status_code == 201

    print (f"KAFKA_CONNECT: CONNECTOR {data['name']} LOADED")


def load_kafka_connectors():
    for file in SINK_CONFIGURATION_FILES:
        _load_connector(file)

if __name__ == "__main__":
    load_kafka_connectors()
