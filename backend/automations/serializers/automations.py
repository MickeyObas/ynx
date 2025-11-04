from rest_framework import serializers
from ..models import Automation

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
