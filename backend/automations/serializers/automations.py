from rest_framework import serializers
from automations.models import Automation, Trigger, Integration

class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = [
            "id",
            "workspace",
            "name",
            "owner",
            "status",
            "trigger",
            "settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at", "workspace"]


class TriggerSerializer(serializers.ModelSerializer):
    """
    Serializer for Automation triggers.
    Handles webhook, polling, or scheduled triggers.
    """

    integration_id = serializers.CharField()
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Trigger
        fields = [
            "id",
            "automation",
            "type",
            "type_display",
            "integration_id",
            "trigger_key",
            "config",
            "connection",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "automation"]
        write_only_fields = ["integration_id", "trigger_key"]

    def validate_integration_id(self, value):
        if not Integration.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Integration '{value}' is not supported")
        return value

    def validate(self, data):
        """
        Optional: Add simple safety checks before saving.
        """
        trigger_type = data.get("type")
        integration_id = data.get("integration_id")
        trigger_key = data.get("trigger_key")

        # Example: webhook triggers might not need integration_id
        if trigger_type != Trigger.Type.SCHEDULE:
            if not integration_id or not trigger_key:
                raise serializers.ValidationError(
                    "integration_id and trigger_key are required for non-schedule triggers."
                )

        return data
    
    def create(self, validated_data):
        integration_id = validated_data.pop("integration_id")
        integration = Integration.objects.get(id=integration_id)
        return Trigger.objects.create(integration=integration, **validated_data)