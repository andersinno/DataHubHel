from collections import OrderedDict

from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datahubhel.core.models import Datastream
from datahubhel.core.serializers import DatastreamSerializer

from .models import Service, ServiceToken, Subscription


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    keys = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='servicetoken-detail',
    )
    allowed_permissions = serializers.SerializerMethodField()
    datastreams = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            'id',
            'url',
            # 'maintainers',
            'name',
            'description',
            'keys',
            'datastreams',
            'allowed_permissions',
        )

    def get_allowed_permissions(self, instance):
        user = self.context['request'].user
        allowed_dstream = Datastream.objects.filter(
            id__in=list(
                instance.client.clientpermission.values_list(
                    'object_pk', flat=True
                )
            ),
            owner=user
        )
        return DatastreamSerializer(
            allowed_dstream,
            many=True,
            context=self.context
        ).data

    def get_datastreams(self, instance):
        user = self.context['request'].user
        datastream = Datastream.objects.filter(owner=user)
        return DatastreamSerializer(
            datastream,
            many=True,
            context=self.context).data


class ServiceKeySerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = ServiceToken
        fields = (
            'id',
            'url',
            'service',
            'key',
        )


class SerializerPermissionSerializer(serializers.Serializer):
    # TODO Accept STS entity ids instead of internal ids
    PERMISSION_CHOICES = [
        ('view_datastream', 'View datastream'),
    ]
    ENTITY_CHOICES = [
        ('datastream', 'Datastream'),
    ]
    ENTITY_MODEL_MAP = {
        'datastream': Datastream,
    }

    service = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='service-detail',
        queryset=Service.objects.all(),
    )

    permission = serializers.ChoiceField(
        choices=PERMISSION_CHOICES,
    )
    entity_type = serializers.ChoiceField(
        choices=ENTITY_CHOICES
    )
    entity_id = serializers.CharField()

    url = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='servicepermission-detail',
        read_only=True,
    )

    id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
    )

    class Meta:
        fields = (
            'service',
            'permission',
            'entity_type',
            'entity_id',
            'url',
        )

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        service = validated_data['service']
        entity_model = self.ENTITY_MODEL_MAP[validated_data['entity_type']]

        entity = entity_model.objects.filter(
            sts_id=validated_data['entity_id'],
            owner=user
        ).first()

        if not entity:
            raise ValidationError({
                'entity_id': [_('No such entity')]
            })

        return service.client.create_perm(
            validated_data['permission'], entity, user)

    def to_representation(self, instance):
        fields = self.fields
        service = instance.client.service
        permission = instance.permission.codename
        entity_id = instance.object_pk

        model_name = str(instance.content_type.model)
        entity_type = model_name

        ret = OrderedDict()
        ret['url'] = fields['url'].to_representation(instance)
        ret['id'] = fields['id'].to_representation(instance)
        ret['service'] = fields['service'].to_representation(service)
        ret['permission'] = fields['permission'].to_representation(permission)
        ret['entity_id'] = fields['entity_id'].to_representation(entity_id)
        ret['entity_type'] = (
            fields['entity_type'].to_representation(entity_type))

        return ret


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'service',
        )
        read_only_fields = ('service',)


class SubscriptionCreateSerializer(
    serializers.HyperlinkedModelSerializer
):
    service = serializers.CharField()

    class Meta:
        model = Subscription
        fields = ('service',)

    def _create_permission(self):
        permission = self.context.get('permission')
        service_url = self.context.get('service_url')
        input_data = {}
        for id_ in permission:
            input_data.update({
                'entity_type': 'datastream',
                'service': service_url,
                'entity_id': id_,
                'permission': 'view_datastream'
            })
            ser = SerializerPermissionSerializer(
                data=input_data,
                context=self.context)

            if ser.is_valid(raise_exception=True):
                ser.save()

    @transaction.atomic
    def create(self, validated_data):
        self._create_permission()
        request = self.context.get('request')
        service_id = validated_data.pop('service')
        validated_data['service_id'] = service_id
        user = request.user
        validated_data['subscriber'] = user
        instance = super().create(validated_data)
        return instance

    def validate_service(self, value):
        request = self.context.get('request')
        if Subscription.objects.filter(
                subscriber=request.user,
                service_id=value).exists():
            raise ValidationError(
                {
                    'service': _(
                        'This service already exists in your subscription')
                }
            )
        return value
