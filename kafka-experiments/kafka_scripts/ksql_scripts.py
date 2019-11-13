import logging
import time
import os

import requests
from confluent_kafka import avro

from . import settings
from .http_response_check import check_errors
from .kafka_utils import create_topic, register_schema

LOG = logging.getLogger(__name__)

data_dir = os.path.abspath(os.path.dirname(__file__))

headers = {
    'Accept': 'application/vnd.ksql.v1+json',
    'Content-Type': 'application/vnd.ksql.v1+json; charset=utf-8'
}


def create_ksql_streams():
    _create_noise_topic()
    _create_noise_stream()
    _create_sensor_name_keyed_stream()
    _create_loud_noise_stream()
    _create_min_value_table()
    _create_open311_topic()
    _create_location_based_steam()

    _create_observation_stream()
    _create_observation_keyed_stream()

    _create_datastream_stream()
    _create_datastream_rekeyed()
    _create_datastream_rekeyed_table()

    _create_datastream_joined_observation()

    _create_thing_stream()
    _create_thing_stream_rekeyed()
    _create_thing_rekeyed_table()

    _create_location_stream()
    _create_location_stream_rekeyed()
    _create_location_rekeyed_table()

    _create_dstream_j_observation_j_thing()

    _create_location_enriched_observation()


def _create_noise_topic():
    if _has_topic(settings.KAFKA_TOPIC):
        return

    create_topic(settings.KAFKA_TOPIC)
    LOG.info("Created Kafka topic: %s", settings.KAFKA_TOPIC)

    key_schema = _get_schema("schema_key.avsc")
    value_schema = _get_schema("schema_nested_value.avsc")
    register_schema(settings.KAFKA_TOPIC, "key", key_schema)
    LOG.info("Created schema for %s-key", settings.KAFKA_TOPIC)
    register_schema(settings.KAFKA_TOPIC, "value", value_schema)
    LOG.info("Created schema for %s-value", settings.KAFKA_TOPIC)


def _get_schema(filename):
    return avro.load(os.path.join(data_dir, filename))


def _create_noise_stream():
    """
    Create the base stream from the noise topic.

    This is the base of all other topics/streams/table
    """
    if _has_stream(settings.NOISE_STREAM):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.NOISE_STREAM}"
        f" WITH (kafka_topic='{settings.KAFKA_TOPIC}',"
        f" value_format='{settings.VALUE_FORMAT}');")
    LOG.info('Created KSQL stream: %s', settings.NOISE_STREAM)


def _create_location_based_steam():
    """
    Create the stream with location for elasticsearch
    """
    if _has_stream('ELASTIC_LOCATION_STREAM'):
        return

    _execute_ksql_commands(
        f"CREATE STREAM ELASTIC_LOCATION_STREAM"
        f" AS SELECT SENSOR->SENSOR_NAME AS SENSOR_NAME,"
        f" THING->LOCATION AS LOCATION"
        f" FROM {settings.NOISE_STREAM}"
        f" PARTITION BY SENSOR_NAME;")
    LOG.info('Created KSQL stream: %s', 'ELASTIC_LOCATION_STREAM')


def _create_sensor_name_keyed_stream():
    """
    Create the stream with key (sensor_name).

    The key part is required if we want to save the message to database.
    """
    if _has_stream(settings.NOISE_STREAM_KEYED):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.NOISE_STREAM_KEYED}"
        f" AS SELECT SENSOR->SENSOR_NAME AS SENSOR_NAME,"
        f" RESULTS->LEVEL AS LEVEL,"
        f" RESULTS->BATTERY AS BATTERY,"
        f" RESULTS->POWER AS POWER,"
        f" RESULTS->OVERLOAD AS OVERLOAD,"
        f" THING->THING_NAME AS THING_NAME,"
        f" THING->LOCATION[0] AS LON,"
        f" THING->LOCATION[1] AS LAT"
        f" FROM {settings.NOISE_STREAM}"
        f" PARTITION BY SENSOR_NAME;")
    LOG.info('Created KSQL stream: %s', settings.NOISE_STREAM_KEYED)


def _create_min_value_table():
    if _has_table(settings.MIN_VALUE_TABLE):
        return

    _check_stream_create_status(settings.NOISE_STREAM_KEYED)
    _execute_ksql_commands(
        f"CREATE TABLE {settings.MIN_VALUE_TABLE} AS"
        f" SELECT SENSOR_NAME, MIN(BATTERY) AS BATTERY FROM"
        f" {settings.NOISE_STREAM_KEYED} GROUP BY sensor_name;")
    LOG.info('Created KSQL table: %s', settings.MIN_VALUE_TABLE)


def _create_open311_topic():
    """
    Create a stream that captures noise levels over 7.0.
    """
    if _has_stream(settings.ALERT_TOPIC):
        return

    _check_stream_create_status(settings.NOISE_STREAM)
    _execute_ksql_commands(
        f"CREATE STREAM {settings.ALERT_TOPIC} AS"
        f" SELECT * FROM {settings.NOISE_STREAM} WHERE"
        f" RESULTS->LEVEL > 7.0 AND RESULTS->OVERLOAD = True;")
    LOG.info('Created KSQL stream: %s', settings.ALERT_TOPIC)


def _create_loud_noise_stream():
    """
    Create a stream that captures noise levels over 4.0.
    """
    if _has_stream(settings.LOUD_NOISE_TOPIC):
        return

    _check_stream_create_status(settings.NOISE_STREAM)
    _execute_ksql_commands(
        f"CREATE STREAM {settings.LOUD_NOISE_TOPIC}"
        f" AS SELECT * from {settings.NOISE_STREAM_KEYED}"
        f" WHERE LEVEL > 4.0;")
    LOG.info('Created KSQL stream: %s', settings.LOUD_NOISE_TOPIC)


def _create_observation_stream():
    """
    Create the base stream from the fi.fvh.observations.noise.ta120
    topic.

    This is the base of all other topics/streams/table
    """
    if _has_stream(settings.OBSERVATION_STREAM):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.OBSERVATION_STREAM}"
        f" WITH (kafka_topic='fi.fvh.observations.noise.ta120',"
        f" value_format='{settings.VALUE_FORMAT}');"
    )
    LOG.info('Created KSQL stream: %s', settings.OBSERVATION_STREAM)


def _create_observation_keyed_stream():
    if _has_stream(settings.PERSISTENT_OBSERVATION_STREAM):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.PERSISTENT_OBSERVATION_STREAM}"
        f" AS SELECT * FROM {settings.OBSERVATION_STREAM}"
        f" PARTITION BY ID;"
    )
    LOG.info('Created KSQL stream: %s', settings.PERSISTENT_OBSERVATION_STREAM)


def _create_datastream_stream():
    if not _has_topic(settings.DATASTREAM_TOPIC):
        time.sleep(4)
        _create_datastream_stream()

    if _has_stream(settings.DATASTREAM_STREAM):
        return

    _execute_ksql_commands(
        f" CREATE STREAM {settings.DATASTREAM_STREAM} WITH"
        f" (KAFKA_TOPIC='{settings.DATASTREAM_TOPIC}',"
        f" VALUE_FORMAT='{settings.VALUE_FORMAT}');"
    )
    LOG.info('Created KSQL stream: %s', settings.DATASTREAM_STREAM)


def _create_datastream_rekeyed():
    if _has_stream(settings.DATASTREAM_REKEYED):
        return

    _execute_ksql_commands(
        f"SET 'auto.offset.reset'='earliest';"
        f" CREATE STREAM {settings.DATASTREAM_REKEYED}"
        f" AS SELECT * FROM {settings.DATASTREAM_STREAM}"
        f" PARTITION BY ID;"
    )
    LOG.info('Created KSQL stream: %s', settings.DATASTREAM_REKEYED)


def _create_datastream_rekeyed_table():
    # Create a table from the rekeyed datastream stream
    if _has_table(settings.DATASTREAM_TABLE):
        return

    _wait_until_rekeyed_stream_is_populated(stream="DATASTREAM_REKEYED")
    _execute_ksql_commands(
        f" CREATE TABLE {settings.DATASTREAM_TABLE}"
        f" WITH (KAFKA_TOPIC='{settings.DATASTREAM_REKEYED}',"
        f" VALUE_FORMAT='{settings.VALUE_FORMAT}', KEY='ID');"
    )
    LOG.info('Created KSQL table: %s', settings.DATASTREAM_TABLE)


def _create_datastream_joined_observation():
    # Create a join of datastream and observation
    if _has_stream(settings.DSTREAM_JOINED_OBS):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.DSTREAM_JOINED_OBS}"
        f" AS SELECT D.ID AS DATASTREAM,"
        f" D.THING_ID AS THING, O.VALUE AS VALUE,"
        f" O.TIME AS TIME, O.ID AS ID"
        f" FROM {settings.OBSERVATION_STREAM} O INNER JOIN"
        f" {settings.DATASTREAM_TABLE} D ON O.DATASTREAM = D.ID;"
    )
    LOG.info('Created KSQL stream: %s', settings.DSTREAM_JOINED_OBS)


def _create_thing_stream():
    # Create thing stream
    if _has_stream(settings.THING_STREAM):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.THING_STREAM} WITH"
        f" (KAFKA_TOPIC='{settings.THING_TOPIC}',"
        f" VALUE_FORMAT='{settings.VALUE_FORMAT}');"
    )
    LOG.info('Created KSQL stream: %s', settings.THING_STREAM)


def _create_thing_stream_rekeyed():
    # Rekey the thing_stream
    if _has_stream(settings.THING_STREAM_REKEY):
        return
    _execute_ksql_commands(
        f"SET 'auto.offset.reset'='earliest';"
        f"CREATE STREAM {settings.THING_STREAM_REKEY}"
        f" AS SELECT * FROM {settings.THING_STREAM} PARTITION BY ID;"
    )
    LOG.info('Created KSQL stream: %s', settings.THING_STREAM_REKEY)


def _create_thing_rekeyed_table():
    # Create a table from thing
    if _has_table(settings.THING_TABLE):
        return
    # Before creating a table we have to make sure that the topic
    # have atleast one message on it. We can't create table from
    # topic with empty values. The kafka takes some time to populate
    # the rekeyed topic, therefore wait unit it is populated.
    _wait_until_rekeyed_stream_is_populated(stream=settings.THING_STREAM_REKEY)
    _execute_ksql_commands(
        f"CREATE TABLE {settings.THING_TABLE} WITH"
        f" (KAFKA_TOPIC='{settings.THING_STREAM_REKEY}',"
        f" VALUE_FORMAT='{settings.VALUE_FORMAT}', KEY='ID');"
    )
    LOG.info('Created KSQL table: %s', settings.THING_TABLE)


def _create_location_stream():
    # Create location stream
    if _has_stream(settings.LOCATION_STREAM):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.LOCATION_STREAM} WITH"
        f" (KAFKA_TOPIC='{settings.LOCATION_TOPIC}',"
        f" VALUE_FORMAT='{settings.VALUE_FORMAT}');"
    )
    LOG.info('Created KSQL stream: %s', settings.LOCATION_STREAM)


def _create_location_stream_rekeyed():
    if _has_stream(settings.LOCATION_REKEY):
        return
    _execute_ksql_commands(
        f"SET 'auto.offset.reset'='earliest';"
        f" CREATE STREAM {settings.LOCATION_REKEY} AS SELECT * FROM"
        f" {settings.LOCATION_STREAM} PARTITION BY ID;"
    )
    LOG.info('Created KSQL stream: %s', settings.LOCATION_REKEY)


def _create_location_rekeyed_table():
    if _has_table(settings.LOCATION_TABLE):
        return
    _wait_until_rekeyed_stream_is_populated(stream=settings.LOCATION_REKEY)
    _execute_ksql_commands(
        f"CREATE TABLE {settings.LOCATION_TABLE} WITH"
        f" (KAFKA_TOPIC='{settings.LOCATION_REKEY}',"
        f" VALUE_FORMAT='{settings.VALUE_FORMAT}', KEY='ID');"
    )
    LOG.info('Created KSQL table: %s', settings.LOCATION_TABLE)


def _create_dstream_j_observation_j_thing():
    if _has_stream(settings.ENRICHED_OBSERVATION):
        return
    _execute_ksql_commands(
        f"CREATE STREAM {settings.ENRICHED_OBSERVATION} AS"
        f" SELECT DJO.DATASTREAM AS DATASTREAM,"
        f" DJO.THING AS THING, DJO.VALUE AS VALUE, DJO.TIME AS TIME,"
        f" DJO.ID AS ID,"
        f" TT.LOCATION_ID AS LOCATION FROM"
        f" {settings.DSTREAM_JOINED_OBS} DJO INNER JOIN"
        f" THING_TABLE TT ON DJO.THING = TT.ID;"
    )
    LOG.info('Created KSQL stream: %s', settings.ENRICHED_OBSERVATION)


def _create_location_enriched_observation():
    if _has_stream(settings.LOCATION_ENRICHED_OBS):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.LOCATION_ENRICHED_OBS} AS"
        f" SELECT EO.THING AS THING,"
        f" EO.VALUE AS VALUE, EO.TIME AS TIME, EO.ID AS ID,"
        f" EO.DATASTREAM AS DATASTREAM, "
        f" LT.NAME AS ADDRESS FROM {settings.ENRICHED_OBSERVATION} EO"
        f" INNER JOIN LOCATION_TABLE LT ON EO.LOCATION = LT.ID;"
    )
    LOG.info('Created KSQL stream: %s', settings.LOCATION_ENRICHED_OBS)


def _has_stream(name):
    return _has_object('stream', name)


def _has_table(name):
    return _has_object('table', name)


def _has_topic(name):
    return _has_object('topic', name)


def _has_object(kind, name):
    if name in _get_names(kind):
        LOG.info(f'{kind.title()} already exists: %s', name)
        return True
    else:
        return False


def _get_names(kind):
    assert kind in ['stream', 'table', 'topic']
    response = _execute_ksql_commands(f'SHOW {kind.upper()}S;')
    data = response.json()
    return [x['name'] for x in data[0][kind + 's']]


def _execute_ksql_commands(command, run_query=False):
    post_url = 'query' if run_query else 'ksql'
    url = f"{settings.KSQL_URL}/{post_url}"
    data = {
        'ksql': command,
        'streamsProperties': {'ksql.streams.auto.offset.reset': 'earliest'},
    }
    response = requests.post(url, headers=headers, json=data)
    check_errors(response)
    return response


def _check_stream_create_status(stream=None):
    assert stream
    url = f'{settings.KSQL_URL}/status/stream/{stream}/create'
    response = requests.get(url)
    assert response.json()['status'] == 'SUCCESS'


def _wait_until_rekeyed_stream_is_populated(stream=None):
    resp = _execute_ksql_commands(
        f"SELECT * FROM {stream} LIMIT 1;", run_query=True
    )
    if not resp:
        time.sleep(5)
        _wait_until_rekeyed_stream_is_populated(stream=stream)
    resp.raise_for_status()


if __name__ == '__main__':
    create_ksql_streams()
