from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from datahubhel.auth.models import ClientPermission
from datahubhel.core.models import Datastream
from datahubhel.service.permissions import ServicePermissions

from .models import Service, ServiceToken, Subscription
from .serializers import (
    SerializerPermissionSerializer,
    ServiceKeySerializer,
    ServiceSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [
        ServicePermissions,
    ]


class ServiceTokenViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceKeySerializer

    def get_queryset(self):
        user = self.request.user
        keys = ServiceToken.objects.filter(
            service__maintainers__in=[user]
        )
        return keys


class ServicePermissionsViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    queryset = ClientPermission.objects.filter(
        client__service__in=Service.objects.all())
    serializer_class = SerializerPermissionSerializer

    def get_queryset(self):
        user = self.request.user
        client = user.client

        q_filters = Q(client=client)
        if isinstance(user, get_user_model()):
            q_filters |= Q(permitted_by=user)

        return ClientPermission.objects.filter(q_filters)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Serialize all subscriptions and provide methods to create new
    subscriptions and terminate old ones. Also allow to update
    the permissions to the datastreams.
    """

    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Remove all the related permissions when the subscription
        # is deleted.
        instance.service.client.clientpermission.all().delete()
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return SubscriptionCreateSerializer
        return SubscriptionSerializer

    def get_serializer_context(self):
        permission = self.request.data.get('permission')
        service_url = self.request.data.get('service_url')
        context = super(SubscriptionViewSet, self).get_serializer_context()
        context.update({'permission': permission, 'service_url': service_url})
        return context

    @action(detail=False, methods=['post'])
    def update_datastream_permission(self, request):
        """
        * Create the permission for the new datastream if it doesn't
          exists in the currently allowed permissions.
        * Delete the permission that is not in the list user has send
          but exists in the currently allowed permissions.
        * Don't do anything about the datastream that exists in both
          the list user sends and currently allowed permissions.
        """
        permission_data = request.data['permission_data']
        service_id = permission_data['serviceId']
        service_url = permission_data['service_url']
        consented_datastream_ids = permission_data['allowed_datastream_ids']
        user_owned_datastream_ids = list(Datastream.objects.filter(
            sts_id__in=consented_datastream_ids,
            owner=self.request.user
            ).values_list('id', flat=True))
        service = Service.objects.get(id=service_id)

        datastream_not_to_delete = service.client.clientpermission.filter(
            object_pk__in=user_owned_datastream_ids)
        datastream_ids_not_to_delete = [
            dstream.content_object.sts_id for
            dstream in datastream_not_to_delete]
        permission_to_be_created = filter(
            lambda item_id: item_id not in datastream_ids_not_to_delete,
            consented_datastream_ids)

        service.client.clientpermission.filter(
            ~Q(object_pk__in=user_owned_datastream_ids)
        ).all().delete()

        input_data = {}
        for perm_id in permission_to_be_created:
            input_data.update({
                'entity_type': 'datastream',
                'service': service_url,
                'entity_id': perm_id,
                'permission': 'view_datastream'
            })
            ser = SerializerPermissionSerializer(
                data=input_data, context=self.get_serializer_context())
            if ser.is_valid(raise_exception=True):
                ser.save()
        return self.list(request)
