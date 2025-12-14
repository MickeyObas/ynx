from rest_framework import serializers
from automations.models import Connection, Integration, Workspace


class ConnectionSerializer(serializers.ModelSerializer):
    # Accept workspace ID from request
    integration_id = serializers.CharField(write_only=True)
    workspace_id = serializers.CharField(write_only=True)

    class Meta:
        model = Connection
        fields = [
            "id",
            "display_name",
            "config",
            "secrets",
            "status",
            "integration_id",
            "workspace_id",
        ]

    def validate(self, attrs):
        integration_id = attrs.get("integration_id")
        workspace_id = attrs.get("workspace_id")
        config = attrs.get("config", {})
        secrets = attrs.get("secrets", {})

        # -------------------------
        # 1. Validate Integration
        # -------------------------
        try:
            integration = Integration.objects.get(id=integration_id)
        except Integration.DoesNotExist:
            raise serializers.ValidationError({"integration_id": "Invalid integration ID."})

        # -------------------------
        # 2. Validate Workspace
        # -------------------------
        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            raise serializers.ValidationError({"workspace_id": "Invalid workspace ID."})

        # -------------------------
        # 3. Validate config using config_schema6
        # -------------------------
        schema = integration.config_schema or {}
        config_errors = {}

        for field, rules in schema.items():
            field_required = rules.get("required", False)

            # Missing?
            if field_required and field not in config and field not in secrets:
                config_errors[field] = "This field is required."

            # Type check (optional)
            if field in config:
                expected_type = rules.get("type")
                if expected_type == "string" and not isinstance(config[field], str):
                    config_errors[field] = "Must be a string."
                elif expected_type == "number" and not isinstance(config[field], (int, float)):
                    config_errors[field] = "Must be a number."

        if config_errors:
            raise serializers.ValidationError({"config": config_errors})

        # Save resolved objects for create()
        attrs["integration"] = integration
        attrs["workspace"] = workspace
        return attrs

    def create(self, validated_data):
        validated_data.pop("integration_id")
        validated_data.pop("workspace_id")

        integration = validated_data.pop("integration")
        workspace = validated_data.pop("workspace")

        return Connection.objects.create(
            integration=integration,
            workspace=workspace,
            **validated_data
        )
