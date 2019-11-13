import datetime

import pytest
from django.db import connection
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from datahubhel.sta.models import Observation
from datahubhel.utils.tests.utils import create_observation, get_datastream

CREATE_OBSERVATION_TABLE = """
    CREATE TABLE IF NOT EXISTS observation (
        id TEXT PRIMARY KEY,
        time BIGINT,
        value TEXT,
        datastream INTEGER
    )
"""
pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestAPIVerbs:
    def setup_method(self, method):
        with connection.cursor() as cursor:
            cursor.execute(CREATE_OBSERVATION_TABLE)

    def _check_observation_properties_key(self, observation):
        required_observation_keys = {"id", "time", "value", "datastream"}
        assert set(observation.keys()) == required_observation_keys

    def test_observation_list_returns_all_observations(self, api_staff_client):
        create_observation("noise_level")
        create_observation("battery")
        url = reverse("datahubhel.sta:observation-list")
        response = api_staff_client.get(url)
        json_response = response.json()
        assert response.status_code == HTTP_200_OK
        assert len(json_response) == 2
        for resp in json_response:
            self._check_observation_properties_key(resp)

    def test_observation_detail_view_returns_observation_detail(
        self, api_staff_client
    ):
        observation_noise_level = create_observation("noise_level")
        datastream_one = observation_noise_level.datastream
        url = reverse(
            "datahubhel.sta:observation-detail",
            kwargs={"pk": observation_noise_level.id},
        )
        response = api_staff_client.get(url)
        json_response = response.json()

        assert response.status_code == HTTP_200_OK
        assert json_response["id"] == "1234-XYZ-1234"
        assert json_response["value"] == observation_noise_level.value
        assert json_response["datastream"] == datastream_one.id

    def test_api_returns_404_status_for_non_existing_observation(
        self, api_staff_client
    ):
        create_observation("noise_level")
        url = reverse("datahubhel.sta:observation-detail", kwargs={"pk": -1})
        response = api_staff_client.get(url)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert Observation.objects.count() == 1

    def test_endpoint_returns_all_observations_for_given_datastream(
        self, api_staff_client
    ):
        observation_noise_level = create_observation("noise_level")
        observation_battery = create_observation("battery")
        datastream_id = observation_noise_level.datastream.id
        url = reverse(
            "datahubhel.sta:datastream-observation",
            kwargs={"datastream_id": datastream_id},
        )
        response = api_staff_client.get(url)
        json_response = response.json()[0]

        assert len(response.json()) == 1
        assert json_response["datastream"] == datastream_id
        assert json_response["datastream"] != observation_battery.datastream.id

        for each_observation in response.json():
            self._check_observation_properties_key(each_observation)

    def test_expanded_observation_returns_datastream_details(
        self, api_staff_client
    ):
        observation_noise_level = create_observation("noise_level")
        url = reverse(
            "datahubhel.sta:observation-detail",
            kwargs={"pk": observation_noise_level.id},
        )
        url = "?".join((url, "expand=Datastream"))
        response = api_staff_client.get(url)
        json_response = response.json()

        assert response.status_code == HTTP_200_OK
        assert type(json_response["datastream"]) == dict
        assert sorted(json_response["datastream"].keys()) == sorted(
            ["id", "thing", "sensor", "sts_id", "name", "description", "owner"]
        )

    def test_user_cannot_create_observation_even_with_correct_data(
        self, api_staff_client
    ):
        datastream_two = get_datastream(2)
        post_data = {
            "id": "XYZ-XYZ-123",
            "time": str(datetime.datetime.now()),
            "sensor_id": "ABC-XYZ-123",
            "property_value": {"distance": 49},
            "property_name": "distance_travelled",
            "datastream": datastream_two.pk,
        }
        url = reverse("datahubhel.sta:observation-list")
        response = api_staff_client.post(url, data=post_data, format="json")

        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
        assert Observation.objects.count() == 0

    def test_user_cannot_patch_observation_even_with_correct_data(
        self, api_staff_client
    ):
        observation_noise_level = create_observation("noise_level")
        url = reverse(
            "datahubhel.sta:observation-detail",
            kwargs={"pk": observation_noise_level.id},
        )
        new_data = {"property_name": "new_property"}

        response = api_staff_client.patch(url, data=new_data)

        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED

    def test_user_cannot_delete_observation(self, api_staff_client):
        observation_noise_level = create_observation("noise_level")
        assert Observation.objects.count() == 1
        url = reverse(
            "datahubhel.sta:observation-detail",
            kwargs={"pk": observation_noise_level.id},
        )
        response = api_staff_client.delete(url)

        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
        assert Observation.objects.count() == 1

    def test_api_returns_selected_fields_only_for_observation(
        self, api_staff_client
    ):
        observation_noise_level = create_observation("noise_level")
        selected_fields = ["id", "time"]
        selected_fields_str = ",".join(selected_fields)
        url = reverse(
            "datahubhel.sta:observation-detail",
            kwargs={"pk": observation_noise_level.id},
        )
        url = f"{url}?select={selected_fields_str}"
        response = api_staff_client.get(url)
        json_response = response.json()

        assert response.status_code == HTTP_200_OK
        assert set(json_response.keys()) == set(selected_fields)
        assert "sensor_id" not in json_response

    def test_user_cannot_post_observation_to_datastream(
        self, api_staff_client
    ):
        datastream_two = get_datastream(2)
        data_to_post = {
            "id": "ABC-123",
            "time": str(datetime.datetime.now()),
            "sensor_id": "1",
            "property_name": "prop",
            "property_value": {"prob_name": "prop_value"},
        }

        url = reverse(
            "datahubhel.sta:datastream-observation",
            kwargs={"datastream_id": datastream_two.id},
        )
        response = api_staff_client.post(url, data=data_to_post, format="json")

        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
