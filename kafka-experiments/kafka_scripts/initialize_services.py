from .elastic_search_geopoint_template import map_lat_lng_to_geopoints
from .ksql_scripts import create_ksql_streams
from .load_kafka_connectors import load_kafka_connectors
from .waiting import wait_for_services


def main():
    if not wait_for_services():
        raise SystemExit('Cannot init, since services did not come up')
    map_lat_lng_to_geopoints()
    load_kafka_connectors()
    create_ksql_streams()


if __name__ == '__main__':
    main()
