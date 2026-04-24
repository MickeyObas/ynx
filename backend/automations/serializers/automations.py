from rest_framework import serializers
from automations.models import Automation, Trigger, Integration, Execution, Connection

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
    connection_id = serializers.CharField()
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
            "connection_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "automation"]
        write_only_fields = ["integration_id", "trigger_key", "connection_id"]

    def validate_integration_id(self, value):
        if not Integration.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Integration '{value}' is not supported")
        return value

    def validate(self, data):
        """
        Optional: Add simple safety checks before saving.
        """
        trigger_type = data.get("type")
        trigger_key = data.get("trigger_key")
        integration_id = data.get("integration_id") or self.instance.integration_id
        connection_id = data.get("connection_id") or self.instance.connection_id

        # Example: webhook triggers might not need integration_id
        if trigger_type != Trigger.Type.SCHEDULE:
            if not integration_id or not trigger_key:
                raise serializers.ValidationError(
                    "integration_id and trigger_key are required for non-schedule triggers."
                )
            
        connection_qs = Connection.objects.filter(id=connection_id)
        if not connection_qs.exists():
            raise serializers.ValidationError(
                "invalid connection_id"
            )
        connection_id = connection_qs.first()
        if connection_id.integration_id != integration_id:
            raise serializers.ValidationError("Misconfigured connection")

        return data
    
    def create(self, validated_data):
        integration_id = validated_data.pop("integration_id")
        integration = Integration.objects.get(id=integration_id)
        connection_id = validated_data.pop("connection_id")
        connection = Connection.objects.get(id=connection_id)
        return Trigger.objects.create(integration=integration, connection=connection, **validated_data)


class ExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = [
            "id",
            "automation",
            "status",
            "started_at",
            "finished_at",
            "attempt",
            "error",
            "meta",
            "created_at",
        ]