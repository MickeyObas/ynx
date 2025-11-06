from rest_framework import serializers

from automations.models import Integration
from integrations.registry import INTEGRATION_REGISTRY


class IntegrationSerializer(serializers.ModelSerializer):
    triggers = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    class Meta:
        model = Integration
        fields = [
            "id",
            "name",
            "description",
            "config_schema",
            "oauth_enabled",
            "webhook_supported",
            "triggers",
            "actions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_triggers(self, obj):
        service_cls = INTEGRATION_REGISTRY[obj.id]
        return service_cls.as_dict()["triggers"] if service_cls else {}

    def get_actions(self, obj):
        service_cls = INTEGRATION_REGISTRY[obj.id]
        return service_cls.as_dict()["actions"] if service_cls else {}


class IntegrationThinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = [
            "id",
            "name",
            "oauth_enabled",
            "webhook_supported",
        ]
