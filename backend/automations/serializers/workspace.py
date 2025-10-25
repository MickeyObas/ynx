from rest_framework import serializers
from django.contrib.auth import get_user_model

from automations.models import Workspace, WorkspaceMembership


User = get_user_model()

class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WorkspaceMembership
        fields = ["user", "user_detail", "role", "joined_at"]
        read_only_fields = ["joined_at"]

    def get_user_detail(self, obj):
        return {
            "id": obj.user.id,
            "name": obj.user.full_name,
            "email": getattr(obj.user, "email", None),
        }


class WorkspaceSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    owner_detail = serializers.SerializerMethodField(read_only=True)
    members = WorkspaceMembershipSerializer(source="workspacemembership_set", many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "owner",
            "owner_detail",
            "members",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_owner_detail(self, obj):
        return {
            "id": obj.owner.id,
            "email": getattr(obj.owner, "email", None),
        }

    def create(self, validated_data):
        user = self.context["request"].user
        workspace = Workspace.objects.create(owner=user, **validated_data)

        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceMembership.Role.ADMIN
        )
        return workspace
