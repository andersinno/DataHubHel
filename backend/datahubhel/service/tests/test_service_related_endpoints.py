import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from datahubhel.service.models import Service, Subscription
from datahubhel.utils.tests.utils import (
    get_datastream,
    get_sensor,
    get_thing,
    get_user,
)
from ta120_adapter.models import TA120Sensor

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestServiceEndpoints:
    def setup_method(self):
        self.user = get_user(username="service-user")
        self.service = self._get_service(self.user)
        self.sensor = get_sensor()
        self.thing = get_thing()

    def _get_service(self, user):
        service, _ = Service.objects.get_or_create(
            identifier="ABC123", defaults={"name": "Service One"}
        )
        service.maintainers.set([self.user])
        return service

    def test_service_list_returns_list_of_services(self, api_staff_client):
        Subscription.objects.get_or_create(
            subscriber=self.user, service=self.service
        )

        response = api_staff_client.get(reverse("service-list"))
        json_response = response.json()

        assert response.status_code == HTTP_200_OK
        assert len(json_response) == 1
        assert json_response[0]["id"] == str(self.service.id)
        assert set(json_response[0].keys()) == {
            "allowed_permissions",
            "datastreams",
            "description",
            "id",
            "keys",
            "name",
            "url",
        }

    def test_service_response_returns_attached_datastreams(
        self, api_staff_client, api_user
    ):
        datastream = get_datastream(
            thing=self.thing, sensor=self.sensor, owner=api_user
        )
        Subscription.objects.get_or_create(
            subscriber=self.user, service=self.service
        )

        response = api_staff_client.get(reverse("service-list"))
        json_response = response.json()

        assert response.status_code == HTTP_200_OK
        assert len(json_response) == 1
        assert json_response[0]["id"] == str(self.service.id)
        assert set(json_response[0].keys()) == {
            "allowed_permissions",
            "datastreams",
            "description",
            "id",
            "keys",
            "name",
            "url",
        }
        assert not len(json_response[0]["datastreams"]) == 0
        assert json_response[0]["datastreams"][0]["sts_id"] == str(
            datastream.sts_id
        )

    def test_user_can_subscribe_to_valid_service(
        self, api_staff_client, api_user
    ):
        datastream = get_datastream(
            thing=self.thing, sensor=self.sensor, owner=api_user
        )
        post_data = dict(
            permission=[datastream.sts_id],
            service=self.service.id,
            service_url=reverse(
                "service-detail", kwargs={"pk": self.service.id}
            ),
        )

        response = api_staff_client.post(
            reverse("subscription-list"), data=post_data, format="json"
        )

        assert response.status_code == HTTP_201_CREATED
        assert response.json() == {"service": self.service.name}
        assert Subscription.objects.count() == 1
        assert Subscription.objects.first().subscriber == api_user
        assert Subscription.objects.first().service == self.service

    def test_user_can_change_permission_to_datastreams(
        self, api_staff_client, api_user
    ):
        datastream_lists = []
        for id in range(0, 4):
            datastream_lists.append(
                get_datastream(
                    num=str(id),
                    thing=self.thing,
                    sensor=self.sensor,
                    owner=api_user,
                )
            )
        post_data = dict(
            permission=[datastream.sts_id for datastream in datastream_lists],
            service=self.service.id,
            service_url=reverse(
                "service-detail", kwargs={"pk": self.service.id}
            ),
        )
        api_staff_client.post(
            reverse("subscription-list"), data=post_data, format="json"
        )

        datastream_lists.pop()
        update_data = dict(
            allowed_datastream_ids=[
                datastream.sts_id for datastream in datastream_lists
            ],
            serviceId=self.service.id,
            service_url=reverse(
                "service-detail", kwargs={"pk": self.service.id}
            ),
        )

        url = reverse("subscription-update-datastream-permission")
        api_staff_client.post(
            url, data={"permission_data": update_data}, format="json"
        )

        assert self.service.client.clientpermission.count() == len(
            datastream_lists
        )
        # Check that new permission is for updated datastreams
        assert set(
            self.service.client.clientpermission.values_list(
                "object_pk", flat=True
            )
        ) == set([str(datastream.id) for datastream in datastream_lists])

    def test_sensorlist_returns_list_of_sensors(
        self,
        api_staff_client,
        api_user
    ):
        self.thing.owner = api_user
        self.thing.save()
        ta120NoiseSensor = TA120Sensor.objects.create(
            identifier='ta120',
            key='XXX124',
            sensor=self.sensor,
            thing=self.thing
        )
        response = api_staff_client.get(reverse('sensors-list'))
        json_response = response.json()[0]

        assert response.status_code == HTTP_200_OK
        assert json_response['identifier'] == ta120NoiseSensor.identifier
        assert json_response['key'] == ta120NoiseSensor.key
        assert json_response['name'] == self.sensor.name
        assert set(json_response.keys()) == {
            'description',
            'identifier',
            'key',
            'name'}

    def test_sensorlist_only_returns_sensors_owned_by_user(
        self,
        api_staff_client,
        api_user
    ):
        TA120Sensor.objects.create(
            identifier='ta120',
            key='XXX124',
            sensor=self.sensor,
            thing=self.thing
        )
        response = api_staff_client.get(reverse('sensors-list'))

        assert response.status_code == HTTP_200_OK
        assert response.json() == []
        assert not self.thing.owner == api_user
