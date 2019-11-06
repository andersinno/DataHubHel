import logging
import os
import time

import requests
from confluent_kafka import avro

from . import settings
from .http_response_check import check_errors

LOG = logging.getLogger(__name__)

headers = {
    "Accept": "application/vnd.ksql.v1+json",
    "Content-Type": "application/vnd.ksql.v1+json",
}


def create_observation_stream():
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
    LOG.info("Created KSQL stream: %s", settings.OBSERVATION_STREAM)


def create_persistent_observation_stream():
    if _has_stream(settings.PERSISTENT_OBSERVATION_STREAM):
        return
    # Make sure to change the offset to earliest here so that
    # this stream will be immediately populated with message
    # as soon as it is created.
    _execute_ksql_commands(
        f"SET 'auto.offset.reset'='earliest';"
        f"CREATE STREAM {settings.PERSISTENT_OBSERVATION_STREAM}"
        f" AS SELECT * FROM {settings.OBSERVATION_STREAM}"
        f" PARTITION BY ID;"
    )
    LOG.info("Created KSQL stream: %s", settings.PERSISTENT_OBSERVATION_STREAM)


def _has_stream(stream):
    response = _execute_ksql_commands(f"SHOW STREAMS;")
    data = response.json()
    stream_list = [x["name"] for x in data[0]["streams"]]
    if stream in stream_list:
        LOG.info(f"Stream already exists: %s", stream)
        return True
    else:
        return False


def _execute_ksql_commands(command):
    url = f"{settings.KSQL_URL}/ksql"
    data = {"ksql": command}
    response = requests.post(url, headers=headers, json=data)
    check_errors(response)
    return response


def create_observation_streams():
    create_observation_stream()
    create_persistent_observation_stream()


if __name__ == "__main__":
    create_observation_streams()
