import environ

env = environ.Env()
env.read_env()

VALUE_FORMAT = "AVRO"  # Serialization format for Kafka
OBSERVATION_STREAM = "OBSERVATION_STREAM"
PERSISTENT_OBSERVATION_STREAM = "OBSERVATION"
KAFKA_SERVERS = env.str("KSQL_BOOTSTRAP_SERVERS", "kafka:29092")
SCHEMA_REGISTRY_URL = env.str("KSQL_KSQL_SCHEMA_REGISTRY_URL", "http://schema-registry:8081")
KSQL_URL = env.str("KSQL_URL", "http://ksql-server:8088")
KAFKA_CONNECT_URL = env.str("KAFKA_CONNECT_URL", "http://kafka-connector:8083")

SINK_DATABASE_URL = env.str(
    "SINK_DATABSE_URL", "postgresql://datahubhel-db:5432/datahubhel"
)
ELASTICSEARCH_URL = env.str("ELASTICSEARCH_URL", "http://localhost:9200")
DB_USERNAME = env.str("POSTGRES_USER", "datahubhel")
DB_PASSWORD = env.str("POSTGRES_PASS", "datahubhel")
