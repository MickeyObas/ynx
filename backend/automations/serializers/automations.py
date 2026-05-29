from rest_framework import serializers
from automations.models import Automation, Trigger, Integration, Execution, Connection, Step

class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = [
            "id",
            "workspace",
            "description",
            "name",
            "owner",
            "status",
            "trigger",
            "settings",
            "created_at",
            "updated_at",
            "published_at"
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at", "published_at", "workspace"]


class TriggerSerializer(serializers.ModelSerializer):
    # TODO: Break into duty-specific serializers
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


class StepCreateSerializer(serializers.ModelSerializer):
    automation = serializers.PrimaryKeyRelatedField(
        queryset=Automation.objects.all()
    )

    integration = serializers.PrimaryKeyRelatedField(
        queryset=Integration.objects.all(),
        required=False,
        allow_null=True
    )

    connection = serializers.PrimaryKeyRelatedField(
        queryset=Connection.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Step
        fields = [
            "automation",
            "kind",
            "order",
            "integration",
            "connection",
            "action_name",
            "config",
        ]

    
class StepDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = [
            "id",
            "automation",
            "kind",
            "order",
            "integration",
            "connection",
            "action_name",
            "config",
        ]

class StepUpdateSerializer(serializers.ModelSerializer):
    integration = serializers.PrimaryKeyRelatedField(
        queryset=Integration.objects.all(),
        required=False,
        allow_null=True
    )

    connection = serializers.PrimaryKeyRelatedField(
        queryset=Connection.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Step
        fields = [
            "kind",
            "order",
            "integration",
            "connection",
            "action_name",
            "config",
        ]
        extra_kwargs = {
            "kind": {"required": False},
            "order": {"required": False},
            "action_name": {"required": False},
            "config": {"required": False},
        }

    def validate(self, attrs):
        """
        Cross-field validation for workflow correctness.
        """

        # get current instance values (important for partial updates)
        instance = self.instance

        kind = attrs.get("kind", instance.kind if instance else None)
        action_name = attrs.get(
            "action_name",
            instance.action_name if instance else None
        )
        integration = attrs.get(
            "integration",
            instance.integration if instance else None
        )
        connection = attrs.get(
            "connection",
            instance.connection if instance else None
        )

        # 2. If integration is set, connection should be compatible
        if integration and connection:
            if connection.integration_id != integration.id:
                raise serializers.ValidationError({
                    "connection": "Connection does not belong to selected integration."
                })

        return attrs
    

class PublishAutomationSerializer(serializers.Serializer):
    step_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False  # optional if you derive steps from the automation itself
    )

    def validate_step_ids(self, step_ids):
        automation = self.context['automation']
        automation_step_ids = set(automation.steps.values_list('id', flat=True))
        invalid = [str(sid) for sid in step_ids if sid not in automation_step_ids]

        if invalid:
            raise serializers.ValidationError(
                f"Steps not belonging to this automation: {invalid}"
            )
        return step_ids