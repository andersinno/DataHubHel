import environs

env = environs.Env()
env.read_env()

ALERT_TOPIC = 'OPEN311'  # Topic for alert system
NOISE_STREAM = 'NOISE_STREAM'  # Stream from NOISE topic
KAFKA_TOPIC = 'NOISE'  # Base topic for noise data
VALUE_FORMAT = 'AVRO'  # Serialization format for Kafka
LOUD_NOISE_TOPIC = 'LOUDNOISE'  # Topic for loud noise data
NOISE_STREAM_KEYED = 'NOISE_STREAM_KEYED'  # sensor_name keyed noise stream
MIN_VALUE_TABLE = 'MIN_BATTERY'  # Table to store minimum battery reading

OBSERVATION_STREAM = 'OBSERVATION_STREAM'
PERSISTENT_OBSERVATION_STREAM = 'OBSERVATION'
DATASTREAM_TOPIC = 'ta120_datahubhel_datastream'
DATASTREAM_STREAM = 'DATASTREAM_STREAM'
DATASTREAM_REKEYED = 'DATASTREAM_REKEYED'
DATASTREAM_TABLE = 'DATASTREAM_TABLE'
DSTREAM_JOINED_OBS = 'DATASTREAM_JOINED_OBSERVATION'

THING_TOPIC = 'ta120_datahubhel_thing'
THING_STREAM = 'THING_STREAM'
THING_STREAM_REKEY = 'THING_STREAM_REKEY'
THING_TABLE = 'THING_TABLE'

LOCATION_TOPIC = 'ta120_datahubhel_location'
LOCATION_STREAM = 'LOCATION_STREAM'
LOCATION_REKEY = 'LOCATION_REKEY'
LOCATION_TABLE = 'LOCATION_TABLE'

ENRICHED_OBSERVATION = 'ENRICHED_OBSERVATION'
LOCATION_ENRICHED_OBS = 'LOCATION_ENRICHED_OBS'

KAFKA_SERVERS = env.str('KAFKA_SERVERS', 'localhost:29092')
SCHEMA_REGISTRY_URL = env.str('SCHEMA_REGISTRY_URL', 'http://localhost:8081')
KSQL_URL = env.str('KSQL_URL', 'http://localhost:8088')
KAFKA_CONNECT_URL = env.str('KAFKA_CONNECT_URL', 'http://localhost:8083')

SINK_DATABASE_URL = env.str('SINK_DATABASE_URL',
                            'postgresql://kafka-sink-db/noisedata')

SOURCE_DATABASE_URL = env.str('SOURCE_DATABASE_URL',
                              'postgresql://datahubhel-db/datahubhel')

ELASTICSEARCH_URL = env.str('ELASTICSEARCH_URL', 'http://localhost:9200')
